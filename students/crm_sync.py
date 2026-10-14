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


# ------------------------------------------------------------- section builders


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
    ug = {
        'qualification': 'B.Com',  # agreed default — the website doesn't ask it
        'status': status,
        'institution': (p.institution or 'Not provided')[:150],
        'yearOfPassing': ug_year,
        'medium': MEDIUM.get(p.medium_instruction, 'English'),
    }
    if ug_score is not None:
        ug['score'] = ug_score
        ug['gradeType'] = _grade(p.ug_score_type)
    has_higher = p.higher_education_status == 1
    higher = {'has': True, 'details': (p.higher_qualification or 'Not provided')[:150]} if has_higher else {'has': False}
    return {
        'class10': {'yearOfPassing': y10, 'gradeType': _grade(p.tenth_score_type), 'score': s10,
                    'medium': MEDIUM.get(p.tenth_medium, 'English')},
        'class12': {'yearOfPassing': y12, 'gradeType': _grade(p.twelveth_score_type), 'score': s12,
                    'medium': MEDIUM.get(p.twelveth_medium, 'English')},
        'ug': ug,
        'higherQualification': higher,
    }


def _work(p):
    return {'employmentStatus': EMPLOYMENT.get(p.employement_status, 'Fresher')}


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


# ------------------------------------------------------------------ entry points


def sync_now(p) -> None:
    """Pushes one saved profile (StudentProfile or StudentProfileDraft) to the CRM."""
    if not os.getenv('CRM_CAPTURE_KEY', ''):
        # warning, not info: without LOGGING config only WARNING+ reaches docker logs
        log.warning('CRM sync skipped: CRM_CAPTURE_KEY is not set in the environment')
        return
    mobile = (p.phone or '').strip()
    if not mobile:
        log.info('CRM sync skipped: profile %s has no phone', getattr(p, 'pk', '?'))
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
    log.info('CRM sync done for %s (profile %s)', mobile, getattr(p, 'pk', '?'))


def sync_profile_async(model, pk) -> None:
    """Fire-and-forget: re-fetches the row on the thread and syncs it."""

    def run():
        try:
            instance = model.objects.filter(pk=pk).first()
            if instance:
                sync_now(instance)
        except Exception:  # noqa: BLE001
            log.exception('CRM sync failed for %s %s', model.__name__, pk)

    threading.Thread(target=run, daemon=True).start()
