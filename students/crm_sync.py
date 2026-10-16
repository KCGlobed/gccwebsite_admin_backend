"""
CRM sync — pushes the student profile to the KCGlobed CRM after it is saved
here, so counsellors see what the student filled on the website.

Flow (runs on a background thread, never blocks or fails the website request):
  1. POST personal+guardian, academic, work — one request per section, so one
     invalid section (CRM validates strictly) never blocks the others.
  2. If the CRM has no lead for this mobile (404), the lead is first created
     through the public capture API, then the section is retried once.
  3. Documents are uploaded one by one (aadhaar, PAN, marksheets, photo,
     signature, resume). dob_certificate is the student's 10th certificate,
     so it lands in the CRM's class10_marksheet slot.

Value mappings (gcc integer choices -> CRM strings) live in the tables below.
Known best-effort defaults, agreed with the business:
  - ug.qualification is always 'B.Com' (the website does not ask it)
  - ug.yearOfPassing = 12th year + 3 (not asked either), capped at the current
    year when the status is Completed
Failures are logged (logger 'crm_sync') and swallowed — the website response
must never depend on the CRM being up.

Env: CRM_API_URL, CRM_CAPTURE_KEY (.env).
"""
import logging
import os
import threading
from datetime import date

import requests

log = logging.getLogger('crm_sync')

TIMEOUT = 20

GENDER = {1: 'Male', 2: 'Female', 3: 'Other'}
MEDIUM = {1: 'English', 2: 'Other', 3: 'Other'}  # CRM knows English/Other only; Hindi -> Other
RELATION = {1: 'Mother', 2: 'Father', 3: 'Other'}  # anything else -> Guardian
UG_STATUS = {1: 'Completed', 2: 'Pursuing'}
EMPLOYMENT = {1: 'Fresher', 2: 'Experienced'}
# gcc file field -> CRM document type
DOC_FIELDS = {
    'aadhaar': 'aadhaar',
    'pancard': 'pan',
    'dob_certificate': 'class10_marksheet',  # the 10th certificate doubles as DOB proof
    'twelveth_marksheet': 'class12_marksheet',
    'graduation_certificate': 'graduation_marksheet',
    'photo': 'photo',
    'signature': 'signature',
    'resume': 'resume',
}


def _base_url():
    return (os.getenv('CRM_API_URL', '') or 'https://crm-backend.kcglobed.com').rstrip('/')


def _headers():
    return {'x-api-key': os.getenv('CRM_CAPTURE_KEY', '')}


def _int(value):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def _float(value):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _grade(score_type):
    """gcc stores 'Percentage' or 'CGPA out of 10' (free text) -> CRM 'Percentage'/'CGPA'."""
    text = str(score_type or '').lower()
    if 'percent' in text:
        return 'Percentage'
    if 'cgpa' in text or 'gpa' in text:
        return 'CGPA'
    return 'Percentage'


def _medium_pair(code, other_text=None):
    """gcc medium int -> (CRM medium, mediumOther). The CRM knows English/Other, so
    Hindi (2) becomes Other/'Hindi' and OTHER (3) carries the typed text if any."""
    if code == 2:
        return 'Other', 'Hindi'
    if code == 3:
        return 'Other', (str(other_text).strip()[:100] or None) if other_text else None
    return 'English', None


def _ug_qualification(p):
    """ug_qualification dropdown -> CRM (qualification, qualificationOther).
    'Other' carries the typed text; an unknown value becomes Other/<value>;
    missing (old records) keeps the agreed 'B.Com' default."""
    value = (getattr(p, 'ug_qualification', '') or '').strip()
    other = (getattr(p, 'ug_qualification_other', '') or '').strip()
    if value in ('B.Com', 'BBA', 'BMS'):
        return value, None
    if value == 'Other' or other:
        return 'Other', (other or None) and other[:150]
    if value:
        return 'Other', value[:150]
    return 'B.Com', None


def _months_between(start, end):
    if not start:
        return None
    end = end or date.today()
    months = (end.year - start.year) * 12 + (end.month - start.month)
    return max(months, 0)


def _experiences(p):
    """StudentExperience / StudentExperienceDraft rows -> CRM work.experiences entries."""
    rows = []
    for rel in ('studentexperience_set', 'studentexperiencedraft_set'):
        manager = getattr(p, rel, None)
        if manager is None:
            continue
        try:
            rows = list(manager.all())
        except Exception:  # noqa: BLE001 — unsaved/fake instances have no manager
            rows = []
        if rows:
            break
    out = []
    for r in rows:
        if not (getattr(r, 'company_name', None) or getattr(r, 'position', None)):
            continue
        entry = {
            'organization': (r.company_name or 'Not provided')[:100],
            'designation': (r.position or 'Not provided')[:100],
        }
        if getattr(r, 'area', None):
            entry['functionalArea'] = r.area[:100]
        start, end = getattr(r, 'start_date', None), getattr(r, 'end_date', None)
        if start:
            entry['fromDate'] = start.isoformat()
        if end:
            entry['toDate'] = end.isoformat()
        months = _months_between(start, end)
        if months is not None:  # legacy duration, kept alongside the dates
            entry['experienceYears'] = min(months // 12, 30)
            entry['experienceMonths'] = months % 12
        out.append(entry)
    return out


# ------------------------------------------------------------- section builders


def _personal_partial(p):
    """Draft mode: whatever is filled, nothing required, no fabricated defaults."""
    out = {}
    for attr, key in (('first_name', 'firstName'), ('last_name', 'lastName'), ('email', 'email'),
                      ('phone', 'mobile'), ('state', 'state'), ('city', 'city')):
        value = getattr(p, attr, None)
        if value:
            out[key] = value
    if p.date_of_birth:
        out['dob'] = p.date_of_birth.isoformat()
    if p.gender:
        out['gender'] = GENDER.get(p.gender, 'Other')
    if p.pincode:
        out['pinCode'] = str(p.pincode).strip()
    if p.address:
        out['address'] = p.address[:250]
    return out


def _guardian_partial(p):
    out = {}
    if p.guardian_name or p.contact_name:
        out['name'] = p.guardian_name or p.contact_name
    if p.guardian_phone or p.contact_phone:
        out['mobile'] = p.guardian_phone or p.contact_phone
    if p.guardian_email:
        out['email'] = p.guardian_email
    if p.guardian_dropdown:
        out['relationship'] = RELATION.get(p.guardian_dropdown, 'Guardian')
        if out['relationship'] == 'Other' and getattr(p, 'guardian_other_reason', None):
            out['relationshipOther'] = p.guardian_other_reason[:100]
    return out


def _school_partial(p, prefix):
    out = {}
    year = _int(getattr(p, f'{prefix}_passing_year', None))
    score = _float(getattr(p, f'{prefix}_passing_percentage', None))
    if year:
        out['yearOfPassing'] = year
    if score is not None:
        out['score'] = score
        out['gradeType'] = _grade(getattr(p, f'{prefix}_score_type', None))
    code = getattr(p, f'{prefix}_medium', None)
    if code:
        out['medium'], medium_other = _medium_pair(code, getattr(p, f'{prefix}_medium_other', None))
        if medium_other:
            out['mediumOther'] = medium_other
    return out


def _academic_partial(p):
    out = {}
    for prefix, name in (('tenth', 'class10'), ('twelveth', 'class12')):
        block = _school_partial(p, prefix)
        if block:
            out[name] = block
    ug = {}
    if getattr(p, 'ug_qualification', None):
        ug['qualification'], q_other = _ug_qualification(p)
        if q_other:
            ug['qualificationOther'] = q_other
    if p.pg_status:
        ug['status'] = UG_STATUS.get(p.pg_status, 'Completed')
    if p.institution:
        ug['institution'] = p.institution[:150]
    if p.medium_instruction:
        ug['medium'], medium_other = _medium_pair(p.medium_instruction, p.other_instruction)
        if medium_other:
            ug['mediumOther'] = medium_other
    score = _float(p.pg_percentage)
    if score is not None:
        ug['score'] = score
        ug['gradeType'] = _grade(p.ug_score_type)
    if ug:
        out['ug'] = ug
    if p.higher_education_status:
        has = p.higher_education_status == 1
        hq = {'has': True, 'details': (p.higher_qualification or 'Not provided')[:150]} if has else {'has': False}
        if has and getattr(p, 'higher_qualification_institution', None):
            hq['institution'] = p.higher_qualification_institution[:150]
        out['higherQualification'] = hq
    return out


def _personal(p):
    required = (p.first_name, p.last_name, p.email, p.phone, p.date_of_birth, p.state, p.city, p.pincode)
    if not all(required):
        return None
    out = {
        'firstName': p.first_name, 'lastName': p.last_name, 'email': p.email, 'mobile': p.phone,
        'dob': p.date_of_birth.isoformat(), 'gender': GENDER.get(p.gender, 'Other'),
        'state': p.state, 'city': p.city, 'pinCode': str(p.pincode).strip(),
    }
    if p.address:
        out['address'] = p.address[:250]
    return out


def _guardian(p):
    name = p.guardian_name or p.contact_name
    phone = p.guardian_phone or p.contact_phone
    if not (name and phone):
        return None
    out = {'name': name, 'relationship': RELATION.get(p.guardian_dropdown, 'Guardian'), 'mobile': phone}
    if out['relationship'] == 'Other' and getattr(p, 'guardian_other_reason', None):
        out['relationshipOther'] = p.guardian_other_reason[:100]
    if p.guardian_email:
        out['email'] = p.guardian_email
    return out


def _academic(p):
    y10, y12 = _int(p.tenth_passing_year), _int(p.twelveth_passing_year)
    s10, s12 = _float(p.tenth_passing_percentage), _float(p.twelveth_passing_percentage)
    ug_score = _float(p.pg_percentage)
    status = UG_STATUS.get(p.pg_status, 'Completed')
    if None in (y10, y12, s10, s12):
        return None  # the CRM academic step is all-or-nothing; partial data would just 400
    if status == 'Completed' and ug_score is None:
        return None  # CRM requires a score once the degree is Completed
    ug_year = y12 + 3  # the website doesn't ask the UG passing year: standard 3-year degree
    if status == 'Completed':
        ug_year = min(ug_year, date.today().year)
    ug_medium, ug_medium_other = _medium_pair(p.medium_instruction, p.other_instruction)
    qualification, qualification_other = _ug_qualification(p)
    ug = {
        'qualification': qualification,
        'status': status,
        'institution': (p.institution or 'Not provided')[:150],
        'yearOfPassing': ug_year,
        'medium': ug_medium,
    }
    if qualification_other:
        ug['qualificationOther'] = qualification_other
    if ug_medium_other:
        ug['mediumOther'] = ug_medium_other
    if ug_score is not None:
        ug['score'] = ug_score
        ug['gradeType'] = _grade(p.ug_score_type)
    has_higher = p.higher_education_status == 1
    higher = {'has': True, 'details': (p.higher_qualification or 'Not provided')[:150]} if has_higher else {'has': False}
    if has_higher and getattr(p, 'higher_qualification_institution', None):
        higher['institution'] = p.higher_qualification_institution[:150]

    def school(year, score, score_type, medium_code, other_text):
        medium, medium_other = _medium_pair(medium_code, other_text)
        block = {'yearOfPassing': year, 'gradeType': _grade(score_type), 'score': score, 'medium': medium}
        if medium_other:
            block['mediumOther'] = medium_other
        return block

    return {
        'class10': school(y10, s10, p.tenth_score_type, p.tenth_medium, getattr(p, 'tenth_medium_other', None)),
        'class12': school(y12, s12, p.twelveth_score_type, p.twelveth_medium, getattr(p, 'twelveth_medium_other', None)),
        'ug': ug,
        'higherQualification': higher,
    }


def _work(p):
    out = {'employmentStatus': EMPLOYMENT.get(p.employement_status, 'Fresher')}
    if out['employmentStatus'] == 'Experienced':
        entries = _experiences(p)
        if entries:
            out['experiences'] = entries
    return out


# ------------------------------------------------------------------- transport


def _post_section(mobile, body, label):
    """POST one section; on 'lead not found' creates the lead via capture and retries once."""
    url = f'{_base_url()}/api/v1/leads/profile-capture'
    response = requests.post(url, json={'mobile': mobile, **body}, headers=_headers(), timeout=TIMEOUT)
    if response.status_code == 404:
        if not _capture_lead(mobile, body):
            return False
        response = requests.post(url, json={'mobile': mobile, **body}, headers=_headers(), timeout=TIMEOUT)
    if response.status_code >= 300:
        log.warning('CRM %s sync failed for %s: %s %s', label, mobile, response.status_code, response.text[:300])
        return False
    return True


def _capture_lead(mobile, body):
    """The CRM has no lead for this student yet — create one through the capture API."""
    personal = body.get('personal') or {}
    payload = {
        'firstName': personal.get('firstName') or 'Website',
        'lastName': personal.get('lastName'),
        'mobile': mobile,
        'email': personal.get('email'),
        'city': personal.get('city'),
        'state': personal.get('state'),
        'source': 'Website',
    }
    response = requests.post(f'{_base_url()}/api/v1/leads/capture',
                             json={k: v for k, v in payload.items() if v}, headers=_headers(), timeout=TIMEOUT)
    if response.status_code >= 300:
        log.warning('CRM lead capture failed for %s: %s %s', mobile, response.status_code, response.text[:300])
        return False
    return True


def _upload_documents(p, mobile):
    url = f'{_base_url()}/api/v1/leads/profile-capture/document'
    for field_name, doc_type in DOC_FIELDS.items():
        field = getattr(p, field_name, None)
        if not field or not getattr(field, 'name', ''):
            continue
        try:
            with field.open('rb') as handle:
                file_name = os.path.basename(field.name)
                response = requests.post(url, data={'mobile': mobile, 'type': doc_type},
                                         files={'file': (file_name, handle)}, headers=_headers(), timeout=60)
            if response.status_code >= 300:
                log.warning('CRM document %s failed for %s: %s %s',
                            doc_type, mobile, response.status_code, response.text[:200])
        except Exception:  # noqa: BLE001 — a missing/corrupt file must not stop the rest
            log.exception('CRM document %s errored for %s', doc_type, mobile)


# --------------------------------------------- CRM -> website (live read overlay)

GENDER_BACK = {'Male': 1, 'Female': 2, 'Other': 3}
RELATION_BACK = {'Mother': 1, 'Father': 2, 'Other': 3}  # CRM 'Guardian' bhi 3 (Other) ban jata hai
UG_STATUS_BACK = {'Completed': 1, 'Pursuing': 2}
EMPLOYMENT_BACK = {'Fresher': 1, 'Experienced': 2}


def _medium_back(block):
    """CRM medium/mediumOther -> (gcc int, other_text)."""
    medium = (block or {}).get('medium')
    other = ((block or {}).get('mediumOther') or '').strip()
    if medium == 'English':
        return 1, None
    if medium == 'Other':
        if other.lower() == 'hindi':
            return 2, None
        return 3, other or None
    return None, None


def fetch_crm_profile(mobile):
    """CRM ka live profile (5s timeout). Koi bhi dikkat -> None, caller apna data dikhaye."""
    key = os.getenv('CRM_READ_KEY', '')
    if not key or not mobile:
        return None
    try:
        response = requests.post(f'{_base_url()}/api/v1/leads/profile-fetch',
                                 json={'mobile': mobile}, headers={'x-api-key': key}, timeout=5)
        if response.status_code >= 300:
            return None
        data = (response.json() or {}).get('data') or {}
        return data if data.get('exists') else None
    except Exception:  # noqa: BLE001 — CRM down must never break the student's page
        log.warning('CRM profile fetch failed for %s', mobile)
        return None


def crm_overrides(crm):
    """CRM profile -> gcc field names/values, sirf bhari hui values. Identity fields
    (email/phone) kabhi override nahi hote — wo website account ke hain."""
    out = {}
    per = crm.get('personal') or {}
    for src, dst in (('firstName', 'first_name'), ('lastName', 'last_name'), ('state', 'state'),
                     ('city', 'city'), ('pinCode', 'pincode'), ('address', 'address'), ('dob', 'date_of_birth')):
        if per.get(src):
            out[dst] = per[src]
    if per.get('gender') in GENDER_BACK:
        out['gender'] = GENDER_BACK[per['gender']]
    g = crm.get('guardian') or {}
    if g.get('name'):
        out['guardian_name'] = g['name']
    if g.get('mobile'):
        out['guardian_phone'] = g['mobile']
    if g.get('email'):
        out['guardian_email'] = g['email']
    if g.get('relationship'):
        out['guardian_dropdown'] = RELATION_BACK.get(g['relationship'], 3)
        if g.get('relationshipOther'):
            out['guardian_other_reason'] = g['relationshipOther']
        elif g['relationship'] == 'Guardian':
            out['guardian_other_reason'] = 'Guardian'
    a = crm.get('academic') or {}
    for block_name, prefix in (('class10', 'tenth'), ('class12', 'twelveth')):
        b = a.get(block_name) or {}
        if b.get('yearOfPassing'):
            out[f'{prefix}_passing_year'] = str(b['yearOfPassing'])
        if b.get('score') is not None:
            out[f'{prefix}_passing_percentage'] = str(b['score'])
        if b.get('gradeType'):
            out[f'{prefix}_score_type'] = b['gradeType']
        code, other = _medium_back(b)
        if code:
            out[f'{prefix}_medium'] = code
        if other:
            out[f'{prefix}_medium_other'] = other
    ug = a.get('ug') or {}
    if ug.get('status') in UG_STATUS_BACK:
        out['pg_status'] = UG_STATUS_BACK[ug['status']]
    if ug.get('score') is not None:
        out['pg_percentage'] = str(ug['score'])
    if ug.get('gradeType'):
        out['ug_score_type'] = ug['gradeType']
    if ug.get('institution'):
        out['institution'] = ug['institution']
    if ug.get('qualification'):
        out['ug_qualification'] = ug['qualification']
    if ug.get('qualificationOther'):
        out['ug_qualification_other'] = ug['qualificationOther']
    code, other = _medium_back(ug)
    if code:
        out['medium_instruction'] = code
    if other:
        out['other_instruction'] = other
    hq = a.get('higherQualification') or {}
    if 'has' in hq:
        out['higher_education_status'] = 1 if hq.get('has') else 2
        if hq.get('details'):
            out['higher_qualification'] = hq['details']
    w = crm.get('work') or {}
    if w.get('employmentStatus') in EMPLOYMENT_BACK:
        out['employement_status'] = EMPLOYMENT_BACK[w['employmentStatus']]
    experiences = w.get('experiences') or []
    if experiences:
        out['user_experience'] = [{
            'company_name': e.get('organization'), 'position': e.get('designation'),
            'area': e.get('functionalArea'), 'start_date': e.get('fromDate'), 'end_date': e.get('toDate'),
        } for e in experiences]
    # CRM ke current documents (signed URLs) -> gcc ke field names, taaki website ke
    # "View Current Document" links CRM ki latest files dikhayen
    docs = crm.get('documents') or {}
    crm_to_gcc_doc = {v: k for k, v in DOC_FIELDS.items()}  # pan->pancard, class10_marksheet->dob_certificate, ...
    for crm_type, meta in docs.items():
        field = crm_to_gcc_doc.get(crm_type)
        if field and (meta or {}).get('url'):
            out[field] = meta['url']
    return out


def fetch_or_create_lead_no(full_name, email, phone):
    """
    Signup (create_student) ke liye CRM ka lead number — application_id yahi banta
    hai, taaki student ka ek hi ID dono systems me chale (Counter sirf CRM ke paas).
    1) lead already hai -> uska leadNo (profile-fetch, READ key)
    2) nahi hai -> capture se bana do (source Website) -> naye lead ka leadNo
    Koi bhi dikkat (CRM down, keys missing, phone nahi) -> None; caller NFET
    fallback use karega — signup kabhi block nahi hota.
    """
    mobile = (phone or '').strip()
    if not mobile:
        return None
    read_key = os.getenv('CRM_READ_KEY', '')
    if read_key:
        try:
            response = requests.post(f'{_base_url()}/api/v1/leads/profile-fetch',
                                     json={'mobile': mobile}, headers={'x-api-key': read_key}, timeout=6)
            if response.status_code < 300:
                lead_no = ((response.json() or {}).get('data') or {}).get('leadNo')
                if lead_no:
                    return lead_no
        except Exception:  # noqa: BLE001
            log.warning('CRM lead-no fetch failed for %s', mobile)
    if not os.getenv('CRM_CAPTURE_KEY', ''):
        return None
    try:
        payload = {'name': (full_name or '').strip() or 'Website Signup', 'mobile': mobile, 'source': 'Website'}
        if email:
            payload['email'] = email
        response = requests.post(f'{_base_url()}/api/v1/leads/capture',
                                 json=payload, headers=_headers(), timeout=8)
        if response.status_code >= 300:
            log.warning('CRM lead capture (signup) failed for %s: %s %s',
                        mobile, response.status_code, response.text[:200])
            return None
        lead = ((response.json() or {}).get('data') or {}).get('lead') or {}
        return lead.get('leadNo')
    except Exception:  # noqa: BLE001
        log.warning('CRM lead capture (signup) errored for %s', mobile)
        return None


# ------------------------------------------------------------------ entry points


def sync_now(p, partial: bool = False) -> None:
    """
    Pushes one saved profile to the CRM.
    partial=True (drafts): sends exactly the fields that are filled, in one
    request with {"partial": true} — the CRM validates field-by-field, drops
    invalid values and merges over what it already has.
    partial=False (final submit): complete sections with strict validation.
    """
    if not os.getenv('CRM_CAPTURE_KEY', ''):
        # warning, not info: without LOGGING config only WARNING+ reaches docker logs
        log.warning('CRM sync skipped: CRM_CAPTURE_KEY is not set in the environment')
        return
    mobile = (p.phone or '').strip()
    if not mobile:
        log.info('CRM sync skipped: profile %s has no phone', getattr(p, 'pk', '?'))
        return

    if partial:
        body = {'partial': True}
        work = _work(p) if getattr(p, 'employement_status', None) else {}  # no default on an unfilled draft
        for key, value in (('personal', _personal_partial(p)), ('guardian', _guardian_partial(p)),
                           ('academic', _academic_partial(p)), ('work', work)):
            if value:
                body[key] = value
        _post_section(mobile, body, 'draft')  # 404 -> capture -> retry handled inside
        _upload_documents(p, mobile)
        log.info('CRM draft sync done for %s (draft %s)', mobile, getattr(p, 'pk', '?'))
        return

    personal, guardian = _personal(p), _guardian(p)
    if personal and guardian:  # the CRM saves these as one step and needs both
        _post_section(mobile, {'personal': personal, 'guardian': guardian}, 'personal')
    else:
        # still make sure the lead exists so academic/work/documents can attach
        _capture_lead(mobile, {'personal': personal or {'firstName': p.first_name, 'lastName': p.last_name,
                                                        'email': p.email, 'city': p.city, 'state': p.state}})
    academic = _academic(p)
    if academic:
        _post_section(mobile, {'academic': academic}, 'academic')
    _post_section(mobile, {'work': _work(p)}, 'work')
    _upload_documents(p, mobile)
    # final submit means the student accepted the declaration — lock it in the CRM too
    # (documents go first: the CRM only accepts a declaration once everything is complete)
    _post_section(mobile, {'declaration': True}, 'declaration')
    log.info('CRM sync done for %s (profile %s)', mobile, getattr(p, 'pk', '?'))


def sync_profile_async(model, pk) -> None:
    """Fire-and-forget: re-fetches the row on the thread and syncs it.
    Drafts (StudentProfileDraft) sync in partial mode — whatever is filled goes."""

    def run():
        try:
            instance = model.objects.filter(pk=pk).first()
            if instance:
                sync_now(instance, partial=model.__name__ == 'StudentProfileDraft')
        except Exception:  # noqa: BLE001
            log.exception('CRM sync failed for %s %s', model.__name__, pk)

    threading.Thread(target=run, daemon=True).start()
