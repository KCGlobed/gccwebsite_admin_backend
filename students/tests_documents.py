"""
/api/students/documents/: several files per type, uploaded one by one and sent to the CRM at once (mocked here).

Run against sqlite with a local settings module (nothing touches the real database or bucket), for example:
    GCC_TEST_NO_MIGRATIONS=1 python manage.py test students.tests_documents --settings=<sqlite settings>
"""
import os
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from students import crm_sync, documents
from students.models import StudentDocument, StudentProfileDraft
from users.models import User

URL = '/api/students/documents/'
ENV = {'CRM_CAPTURE_KEY': 'capture-key', 'CRM_API_URL': 'https://crm.test'}


class FakeResponse:
    def __init__(self, status, body=None):
        self.status_code, self._body, self.text = status, body or {}, str(body)

    def json(self):
        return self._body


def crm_accepts():
    """The CRM's upload endpoint: every file accepted, each with its own id."""
    calls = []

    def post(url, data=None, files=None, headers=None, timeout=None):
        calls.append({'url': url, 'data': dict(data), 'file': files['file'][0]})
        return FakeResponse(201, {'data': {'documentId': f'crm{len(calls):021d}', 'unchanged': False}})
    return post, calls


@mock.patch.dict(os.environ, ENV)
@mock.patch.object(crm_sync, 'fetch_crm_profile', return_value=None)  # the CRM's read API is out of reach unless a test says
class StudentDocumentsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='meera@example.com', first_name='Meera', phone1='9876543210')
        self.draft = StudentProfileDraft.objects.create(user=self.user, phone='9876543210')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def upload(self, doc_type, name, content=b'%PDF-1.4 test'):
        return self.client.post(URL, {'type': doc_type, 'file': SimpleUploadedFile(name, content)}, format='multipart')

    def test_several_files_of_a_type_go_to_the_crm_one_by_one(self, _fetch):
        post, calls = crm_accepts()
        with mock.patch.object(documents.requests, 'post', side_effect=post):
            first = self.upload('aadhaar', 'front.pdf', b'%PDF front')
            second = self.upload('aadhaar', 'back.pdf', b'%PDF back')
            third = self.upload('aadhaar', 'extra.pdf', b'%PDF extra')
        self.assertEqual((first.status_code, second.status_code, third.status_code), (201, 201, 400))
        self.assertIn('at most 2 files', str(third.json()))
        self.assertEqual([c['data'] for c in calls], [{'mobile': '9876543210', 'type': 'aadhaar', 'mode': 'add'}] * 2)
        self.assertEqual([c['file'] for c in calls], ['front.pdf', 'back.pdf'])
        self.assertFalse(second.json()['data']['pending'])
        self.assertEqual(list(StudentDocument.objects.values_list('crm_document_id', flat=True)),
                         ['crm000000000000000000001', 'crm000000000000000000002'])
        self.draft.refresh_from_db()
        self.assertTrue(self.draft.aadhaar.name.startswith(f'student-documents/{self.user.id}/'))  # the first file

    def test_a_single_file_type_replaces_and_follows_into_the_old_column(self, _fetch):
        post, calls = crm_accepts()
        with mock.patch.object(documents.requests, 'post', side_effect=post):
            self.upload('photo', 'old.png', b'old picture')
            self.upload('photo', 'new.png', b'new picture')
        self.assertEqual(list(StudentDocument.objects.filter(is_current=True).values_list('original_name', flat=True)), ['new.png'])
        self.assertNotIn('mode', calls[0]['data'])  # one file per type: the CRM replaces it
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.photo.name, StudentDocument.objects.get(is_current=True).file.name)

    def test_the_same_file_again_adds_nothing(self, _fetch):
        post, calls = crm_accepts()
        with mock.patch.object(documents.requests, 'post', side_effect=post):
            self.upload('other', 'noc.pdf', b'same bytes')
            again = self.upload('other', 'noc copy.pdf', b'same bytes')
        self.assertEqual((again.status_code, again.json()['data']['unchanged']), (200, True))
        self.assertEqual((StudentDocument.objects.count(), len(calls)), (1, 1))

    def test_bad_files_are_refused(self, _fetch):
        self.assertIn('Photograph must be', str(self.upload('photo', 'photo.pdf').json()))
        self.assertIn('at most 2 MB', str(self.upload('pan', 'pan.pdf', b'x' * (2 * 1024 * 1024 + 1)).json()))
        self.assertEqual(self.upload('passport', 'p.pdf').status_code, 400)
        self.assertEqual(self.client.post(URL, {'type': 'pan'}, format='multipart').status_code, 400)
        self.assertFalse(StudentDocument.objects.exists())

    def test_a_file_the_crm_could_not_take_is_sent_with_the_next_save(self, _fetch):
        with mock.patch.object(documents.requests, 'post', side_effect=ConnectionError('CRM down')):
            res = self.upload('class12_marksheet', 'm1.pdf', b'%PDF m1')
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.json()['data']['pending'])
        self.assertIn('CRM down', StudentDocument.objects.get().crm_error)
        # the next profile save: the pending file goes, the old column of that type is not sent again
        post, calls = crm_accepts()
        with mock.patch.object(documents.requests, 'post', side_effect=post), \
                mock.patch.object(crm_sync.requests, 'post', side_effect=post):
            crm_sync._upload_documents(self.draft, '9876543210')
        self.assertEqual([(c['data']['type'], c['file']) for c in calls], [('class12_marksheet', 'm1.pdf')])
        self.assertIsNotNone(StudentDocument.objects.get().crm_document_id)

    def test_the_list_is_the_crms_plus_files_not_yet_sent(self, fetch):
        StudentDocument.objects.create(user=self.user, doc_type='aadhaar', file='student-documents/x/a.pdf',
                                       original_name='synced.pdf', size=1, checksum='a', crm_document_id='crm1')
        StudentDocument.objects.create(user=self.user, doc_type='aadhaar', file='student-documents/x/b.pdf',
                                       original_name='waiting.pdf', size=1, checksum='b')
        StudentDocument.objects.create(user=self.user, doc_type='pan', file='student-documents/x/c.pdf',
                                       original_name='deleted in crm.pdf', size=1, checksum='c', crm_document_id='crm9')
        fetch.return_value = {'exists': True, 'locked': False, 'documents': {'aadhaar': {
            'id': 'crm2', 'fileName': 'by counsellor.pdf', 'url': 'https://r2/c.pdf', 'source': 'crm',
            'files': [{'id': 'crm1', 'fileName': 'synced.pdf', 'url': 'https://r2/a.pdf', 'source': 'website'},
                      {'id': 'crm2', 'fileName': 'by counsellor.pdf', 'url': 'https://r2/c.pdf', 'source': 'crm'}]}}}
        data = self.client.get(URL).json()['data']
        slots = {s['type']: s for s in data['documents']}
        self.assertEqual([(f['fileName'], f['source'], f['pending']) for f in slots['aadhaar']['files']],
                         [('synced.pdf', 'website', False), ('by counsellor.pdf', 'crm', False), ('waiting.pdf', 'website', True)])
        self.assertEqual(slots['pan']['files'], [])  # the CRM deleted it: the student no longer sees it
        self.assertEqual((slots['aadhaar']['maxFiles'], slots['other']['maxFiles'], data['crmSynced']), (2, 10, True))

    def test_a_locked_profile_takes_no_uploads(self, fetch):
        fetch.return_value = {'exists': True, 'locked': True, 'documents': {}}
        res = self.upload('pan', 'pan.pdf')
        self.assertEqual(res.status_code, 400)
        self.assertIn('locked', str(res.json()))

    def test_an_empty_old_column_takes_the_latest_upload_when_the_profile_is_saved(self, _fetch):
        StudentDocument.objects.create(user=self.user, doc_type='signature', file='student-documents/x/s.png',
                                       original_name='s.png', size=1, checksum='s')
        draft = StudentProfileDraft(user=self.user, phone='9876543210')
        documents.fill_missing_files(draft)
        self.assertEqual(draft.signature.name, 'student-documents/x/s.png')

    def test_only_a_signed_in_student(self, _fetch):
        self.assertEqual(APIClient().get(URL).status_code, 401)
