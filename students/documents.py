"""
Student profile documents, several files per type (GET/POST /api/students/documents/).

- types and limits are the CRM's: Aadhaar 2 files, Class 10th / 12th 3, Graduation 10, Other Documents 10; PAN,
  photo, signature and resume one file, which a new upload replaces. Sizes stay the website's: 2 MB, resume 5 MB.
- a file is uploaded the moment the student picks it, and goes to the CRM at once (profile-capture/document,
  mode "add" for the several-file types). A file the CRM could not take stays "pending" and is sent again with the
  next profile save (crm_sync).
- what the student sees is the CRM's list (its counsellors' uploads and deletions included) plus their files still
  pending; without the CRM, their own files. The student cannot delete: only the CRM does.
- the latest file of each type is also kept in the profile's old file column (aadhaar, photo, ...), which the admit
  card, the score card and the reports read.
"""
import hashlib
import logging
import os

import requests
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from . import crm_sync
from .models import StudentDocument, StudentProfile, StudentProfileDraft

log = logging.getLogger('crm_sync')

PDF_IMG = ('.pdf', '.jpg', '.jpeg', '.png')
IMG = ('.jpg', '.jpeg', '.png')
WORD_ALL = ('.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png')
# CRM type -> (label, allowed extensions, max MB, max files, the profile's old file column)
TYPES = {
    'aadhaar': ('Aadhaar Card', PDF_IMG, 2, 2, 'aadhaar'),
    'pan': ('PAN Card', PDF_IMG, 2, 1, 'pancard'),
    'class10_marksheet': ('Class 10th Marksheet', PDF_IMG, 2, 3, 'dob_certificate'),
    'class12_marksheet': ('Class 12th Marksheet', PDF_IMG, 2, 3, 'twelveth_marksheet'),
    'graduation_marksheet': ('Graduation Certificate / Marksheets', PDF_IMG, 2, 10, 'graduation_certificate'),
    'photo': ('Photograph', IMG, 2, 1, 'photo'),
    'signature': ('Signature', IMG, 2, 1, 'signature'),
    'resume': ('Resume', WORD_ALL, 5, 1, 'resume'),
    'other': ('Other Documents', WORD_ALL, 2, 10, None),
}
PUSH_TIMEOUT = 60


def student_mobile(user) -> str:
    """The mobile the CRM knows the student by: the profile's, the draft's, else the signup number."""
    for model in (StudentProfile, StudentProfileDraft):
        row = model.objects.filter(user=user).exclude(phone__isnull=True).exclude(phone='').first()
        if row:
            return row.phone.strip()
    return (getattr(user, 'phone1', None) or '').strip()


def _url(field) -> str | None:
    try:
        return field.url if field else None
    except Exception:  # noqa: BLE001 — a storage hiccup only loses the link
        return None


def _own_json(doc: StudentDocument) -> dict:
    return {'id': f'web-{doc.id}', 'fileName': doc.original_name, 'url': _url(doc.file), 'uploadedAt': doc.created_at,
            'source': 'website', 'pending': not doc.crm_document_id}


def _files(user, crm: dict | None) -> dict[str, list[dict]]:
    """type -> the files the student sees. With the CRM: its current files, then the student's not yet sent."""
    own = list(StudentDocument.objects.filter(user=user, is_current=True).order_by('created_at'))
    out = {t: [] for t in TYPES}
    if crm is not None:
        for doc_type, entry in (crm.get('documents') or {}).items():
            if doc_type in out and entry:
                out[doc_type] = [{'id': f.get('id'), 'fileName': f.get('fileName'), 'url': f.get('url'),
                                  'uploadedAt': f.get('uploadedAt'), 'source': f.get('source') or 'crm', 'pending': False}
                                 for f in (entry.get('files') or [entry])]
        for doc in own:
            if not doc.crm_document_id and doc.doc_type in out:
                out[doc.doc_type].append(_own_json(doc))
        return out
    for doc in own:
        if doc.doc_type in out:
            out[doc.doc_type].append(_own_json(doc))
    # the CRM is out of reach: a type with no upload here still shows the profile's old file
    profile = StudentProfile.objects.filter(user=user).first() or StudentProfileDraft.objects.filter(user=user).first()
    for doc_type, (_, _, _, _, column) in TYPES.items():
        field = getattr(profile, column, None) if profile and column else None
        if not out[doc_type] and field and getattr(field, 'name', ''):
            out[doc_type] = [{'id': f'old-{doc_type}', 'fileName': os.path.basename(field.name), 'url': _url(field),
                              'uploadedAt': None, 'source': 'website', 'pending': False}]
    return out


def list_documents(user) -> dict:
    mobile = student_mobile(user)
    crm = crm_sync.fetch_crm_profile(mobile) if mobile else None
    files = _files(user, crm)
    return {
        'documents': [{'type': t, 'label': label, 'accept': list(exts), 'maxMb': max_mb, 'maxFiles': max_files,
                       'files': files[t]} for t, (label, exts, max_mb, max_files, _) in TYPES.items()],
        'crmSynced': crm is not None,
        'locked': bool(crm and crm.get('locked')),
    }


def _checksum(file) -> str:
    digest = hashlib.sha256()
    for chunk in file.chunks():
        digest.update(chunk)
    file.seek(0)
    return digest.hexdigest()


def _mirror(user, doc: StudentDocument) -> None:
    """The profile's old file column follows the new upload: always for a single-file type, the first file only
    for the others (the admit card, the score card and the reports read these columns)."""
    column = TYPES[doc.doc_type][4]
    if not column:
        return
    single = TYPES[doc.doc_type][3] == 1
    for model in (StudentProfileDraft, StudentProfile):
        for row in model.objects.filter(user=user):
            if single or not getattr(getattr(row, column), 'name', ''):
                setattr(row, column, doc.file.name)
                row.save(update_fields=[column])


def fill_missing_files(row) -> None:
    """Before a profile or draft is saved: an empty old file column takes the student's latest upload of its type."""
    user_id = getattr(row, 'user_id', None)
    if not user_id:
        return
    for doc_type, (_, _, _, max_files, column) in TYPES.items():
        if column and not getattr(getattr(row, column, None), 'name', ''):
            docs = StudentDocument.objects.filter(user_id=user_id, doc_type=doc_type, is_current=True)
            doc = (docs.order_by('-created_at') if max_files == 1 else docs.order_by('created_at')).first()
            if doc:
                setattr(row, column, doc.file.name)


def push(doc: StudentDocument, mobile: str) -> bool:
    """One file to the CRM. True once the CRM holds it (or already did)."""
    if not os.getenv('CRM_CAPTURE_KEY', '') or not mobile:
        return False
    url = f'{crm_sync._base_url()}/api/v1/leads/profile-capture/document'
    data = {'mobile': mobile, 'type': doc.doc_type}
    if TYPES[doc.doc_type][3] > 1:
        data['mode'] = 'add'

    def send():
        with doc.file.open('rb') as handle:
            return requests.post(url, data=data, files={'file': (doc.original_name, handle)},
                                 headers=crm_sync._headers(), timeout=PUSH_TIMEOUT)

    try:
        response = send()
        if response.status_code == 404 and crm_sync._capture_lead(mobile, {}):  # no lead yet: make it, try once more
            response = send()
        if response.status_code >= 300:
            doc.crm_error = f'{response.status_code} {response.text[:280]}'
            doc.save(update_fields=['crm_error'])
            log.warning('CRM document %s failed for %s: %s', doc.doc_type, mobile, doc.crm_error)
            return False
        body = (response.json() or {}).get('data') or {}
    except Exception as exc:  # noqa: BLE001 — the CRM being down must not lose the upload
        doc.crm_error = str(exc)[:300]
        doc.save(update_fields=['crm_error'])
        log.warning('CRM document %s errored for %s: %s', doc.doc_type, mobile, exc)
        return False
    doc.crm_document_id = body.get('documentId') or doc.crm_document_id or 'unknown'
    doc.crm_synced_at = timezone.now()
    doc.crm_error = None
    doc.save(update_fields=['crm_document_id', 'crm_synced_at', 'crm_error'])
    return True


def push_pending(user, mobile: str) -> None:
    """Files the CRM could not take earlier, sent again (crm_sync calls this on every profile save)."""
    for doc in StudentDocument.objects.filter(user=user, is_current=True, crm_document_id__isnull=True).order_by('created_at'):
        push(doc, mobile)


def types_with_uploads(user) -> set[str]:
    """Types the student has uploaded here: crm_sync no longer sends those from the profile's old columns."""
    return set(StudentDocument.objects.filter(user=user).values_list('doc_type', flat=True))


def upload(user, doc_type, file) -> dict:
    if doc_type not in TYPES:
        raise ValidationError({'type': 'Unknown document type'})
    if file is None:
        raise ValidationError({'file': 'Choose a file'})
    label, exts, max_mb, max_files, _ = TYPES[doc_type]
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in exts:
        allowed = '/'.join(e.lstrip('.').upper() for e in exts if e != '.jpeg')
        raise ValidationError({'file': f'{label} must be {allowed}'})
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError({'file': f'{label} can be at most {max_mb} MB'})

    mobile = student_mobile(user)
    crm = crm_sync.fetch_crm_profile(mobile) if mobile else None
    if crm and crm.get('locked'):
        raise ValidationError({'file': 'Your profile is locked after the declaration. Contact your counsellor to change a document.'})
    checksum = _checksum(file)
    with transaction.atomic():
        own = list(StudentDocument.objects.select_for_update().filter(user=user, doc_type=doc_type, is_current=True))
        same = next((d for d in own if d.checksum == checksum), None)
        if same:
            return {**_own_json(same), 'unchanged': True}
        if max_files > 1 and len(_files(user, crm)[doc_type]) >= max_files:
            raise ValidationError({'file': f'{label}: at most {max_files} files can be uploaded'})
        if max_files == 1:
            StudentDocument.objects.filter(pk__in=[d.pk for d in own]).update(is_current=False)
        doc = StudentDocument.objects.create(
            user=user, doc_type=doc_type, file=file, original_name=file.name[:255], size=file.size,
            content_type=(getattr(file, 'content_type', '') or '')[:100], checksum=checksum,
        )
    _mirror(user, doc)
    push(doc, mobile)
    doc.refresh_from_db()
    return {**_own_json(doc), 'unchanged': False}
