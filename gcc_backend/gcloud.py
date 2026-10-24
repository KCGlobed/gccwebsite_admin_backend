"""
File storage backends, served from Cloudflare R2 (S3 compatible); same approach as lmsbackend/gcloud.py.

The module path and class names are kept from the Google Cloud Storage setup so STORAGES in settings.py does not
change. Connection settings come from the AWS_* values in settings.py, which are derived from the R2_* values.
A bucket with a public domain (R2_PUBLIC_DOMAINS) gets plain links; any other gets signed links
(AWS_QUERYSTRING_EXPIRE).
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


def _r2_storage(bucket_name, location=''):
    domain = settings.R2_PUBLIC_DOMAINS.get(bucket_name)
    return S3Boto3Storage(bucket_name=bucket_name, location=location, custom_domain=domain or None,
                          querystring_auth=not domain)


Static = lambda: _r2_storage(settings.R2_STATIC_BUCKET_NAME, 'staticfiles')
Media = lambda: _r2_storage(settings.R2_BUCKET_NAME, 'media')


class GoogleCloudMediaFileStorage(S3Boto3Storage):
    def __init__(self, **kwargs):
        domain = settings.R2_PUBLIC_DOMAINS.get(settings.R2_BUCKET_NAME)
        kwargs.setdefault('bucket_name', settings.R2_BUCKET_NAME)
        kwargs.setdefault('custom_domain', domain or None)
        kwargs.setdefault('querystring_auth', not domain)
        super().__init__(**kwargs)


class GoogleCloudPrivateMediaFileStorage(S3Boto3Storage):
    location = "media"

    def __init__(self, **kwargs):
        kwargs.setdefault('bucket_name', settings.R2_PRIVATE_BUCKET_NAME)
        super().__init__(**kwargs)


class GoogleCloudStaticFileStorage(S3Boto3Storage):
    def __init__(self, **kwargs):
        domain = settings.R2_PUBLIC_DOMAINS.get(settings.R2_STATIC_BUCKET_NAME)
        kwargs.setdefault('bucket_name', settings.R2_STATIC_BUCKET_NAME)
        kwargs.setdefault('custom_domain', domain or None)
        kwargs.setdefault('querystring_auth', not domain)
        super().__init__(**kwargs)


# ---------------------------------------------------------------------------------------------------------------
# Google Cloud Storage setup, kept for rollback: restore this block (and the GCS block in settings.py),
# remove everything above it.
# ---------------------------------------------------------------------------------------------------------------
# from django.conf import settings
# from storages.backends.gcloud import GoogleCloudStorage
# from storages.utils import setting
# from urllib.parse import urljoin
#
# Static = lambda: GoogleCloudStorage(location='staticfiles')
# Media = lambda: GoogleCloudStorage(location='media')
#
#
# class GoogleCloudMediaFileStorage(GoogleCloudStorage):
#     bucket_name = setting('GS_BUCKET_NAME')
#     def url(self, name):
#         return urljoin(settings.MEDIA_URL, name)
#
#
# class GoogleCloudPrivateMediaFileStorage(GoogleCloudStorage):
#     bucket_name = setting('GS_BUCKET_NAME_2')
#     location = "media"
#     def url(self, name):
#         return urljoin(settings.SECURE_MEDIA_URL, name)
#
#
# class GoogleCloudStaticFileStorage(GoogleCloudStorage):
#       bucket_name = setting('GS_STATIC_BUCKET_NAME')
#       def url(self, name):
#             return urljoin(settings.STATIC_URL, name)
