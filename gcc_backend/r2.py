"""
Cloudflare R2 client exposing the part of the google-cloud-storage API used across the views
(client.bucket(...) / get_bucket(...).blob(...) with upload_from_*, exists, delete, cache_control + patch,
public_url and generate_signed_url), so the call sites keep working after the move from Google Cloud Storage.
Same approach as lmsbackend/r2.py.

Bucket names stay the GCS ones from the env (GS_BUCKET_NAME ...). R2 does not allow '_' in a bucket name, so the
R2 buckets were created with '-' instead (gcc_static_files_backend -> gcc-static-files-backend); r2_bucket_name()
maps one to the other.
"""
import math
import mimetypes
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings


def r2_bucket_name(name):
    return (name or '').replace('_', '-')


def _seconds_until(expiration):
    """Accept a datetime, timedelta or seconds, like GCS generate_signed_url."""
    if isinstance(expiration, datetime):
        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=timezone.utc)
        expiration = expiration - datetime.now(timezone.utc)
    if isinstance(expiration, timedelta):
        expiration = expiration.total_seconds()
    # S3 SigV4 allows 1 second to 7 days.
    return max(1, min(int(math.ceil(expiration)), 604800))


class R2Blob:
    def __init__(self, bucket, name):
        self.bucket = bucket
        self.name = name
        self.content_type = None
        self.cache_control = None
        self.content_disposition = None
        self.updated = None

    @property
    def _s3(self):
        return self.bucket.client.s3

    def _extra_args(self):
        extra = {'ContentType': self.content_type or 'application/octet-stream'}
        if self.cache_control:
            extra['CacheControl'] = self.cache_control
        if self.content_disposition:
            extra['ContentDisposition'] = self.content_disposition
        return extra

    def upload_from_filename(self, filename, content_type=None, **kwargs):
        self.content_type = content_type or mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self._s3.upload_file(filename, self.bucket.name, self.name, ExtraArgs=self._extra_args())

    def upload_from_file(self, file_obj, content_type=None, rewind=False, **kwargs):
        if rewind:
            file_obj.seek(0)
        self.content_type = content_type or mimetypes.guess_type(self.name)[0] or 'application/octet-stream'
        self._s3.upload_fileobj(file_obj, self.bucket.name, self.name, ExtraArgs=self._extra_args())

    def upload_from_string(self, data, content_type='text/plain', **kwargs):
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.content_type = content_type
        self._s3.put_object(Bucket=self.bucket.name, Key=self.name, Body=data, **self._extra_args())

    def download_as_bytes(self, **kwargs):
        return self._s3.get_object(Bucket=self.bucket.name, Key=self.name)['Body'].read()

    download_as_string = download_as_bytes

    def download_to_filename(self, filename, **kwargs):
        self._s3.download_file(self.bucket.name, self.name, filename)

    def reload(self, **kwargs):
        head = self._s3.head_object(Bucket=self.bucket.name, Key=self.name)
        self.content_type = head.get('ContentType')
        self.cache_control = head.get('CacheControl')
        self.content_disposition = head.get('ContentDisposition')
        self.updated = head.get('LastModified')

    def exists(self, **kwargs):
        try:
            self.reload()
            return True
        except ClientError as exc:
            if exc.response.get('Error', {}).get('Code') in ('404', 'NoSuchKey', 'NotFound'):
                return False
            raise

    def delete(self, **kwargs):
        self._s3.delete_object(Bucket=self.bucket.name, Key=self.name)

    def patch(self, **kwargs):
        """Saves cache_control / content_type / content_disposition set on the blob. S3 has no metadata-only
        update, so the object is copied onto itself with the new headers."""
        head = self._s3.head_object(Bucket=self.bucket.name, Key=self.name)
        self.content_type = self.content_type or head.get('ContentType')
        self.cache_control = self.cache_control or head.get('CacheControl')
        self.content_disposition = self.content_disposition or head.get('ContentDisposition')
        self._s3.copy_object(
            Bucket=self.bucket.name, Key=self.name, CopySource={'Bucket': self.bucket.name, 'Key': self.name},
            MetadataDirective='REPLACE', Metadata=head.get('Metadata', {}), **self._extra_args(),
        )
        self.reload()

    def generate_signed_url(self, expiration=None, method='GET', version=None, **kwargs):
        if expiration is None:
            expiration = settings.AWS_QUERYSTRING_EXPIRE
        operation = {'GET': 'get_object', 'PUT': 'put_object'}[method.upper()]
        return self._s3.generate_presigned_url(
            operation,
            Params={'Bucket': self.bucket.name, 'Key': self.name},
            ExpiresIn=_seconds_until(expiration),
        )

    @property
    def public_url(self):
        domain = settings.R2_PUBLIC_DOMAINS.get(self.bucket.name)
        if domain:
            return 'https://{}/{}'.format(domain, quote(self.name))
        # Bucket has no public domain: hand out a signed link instead.
        return self.generate_signed_url()


class R2Bucket:
    def __init__(self, client, name):
        self.client = client
        self.name = r2_bucket_name(name)

    def blob(self, name):
        return R2Blob(self, name)


class R2Client:
    def __init__(self):
        self._s3 = None

    @property
    def s3(self):
        if self._s3 is None:
            self._s3 = boto3.client(
                's3',
                endpoint_url=settings.R2_END_POINT,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                region_name='auto',
                config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
            )
        return self._s3

    def get_bucket(self, name):
        return R2Bucket(self, name)

    bucket = get_bucket


client = R2Client()


def file_url(bucket_name, key):
    """Link to an object: plain on a bucket with a public domain, otherwise signed (7 days)."""
    return client.bucket(bucket_name).blob(key).public_url
