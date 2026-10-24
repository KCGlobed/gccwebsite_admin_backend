from django import template
from django.conf import settings
from users.models import *
import math
register = template.Library()
from datetime import datetime, date
from gcc_backend.r2 import file_url


@register.simple_tag
def bucket_static(path):
    """Link to a file in the static bucket on Cloudflare R2: plain with a public domain, otherwise signed."""
    return file_url(settings.GS_STATIC_BUCKET_NAME, path)


@register.filter("convert_comma_format")
def convert_comma_format(activities):
    activities_str = ", ".join(map(str, activities)) if isinstance(activities, list) else str(activities)
    
    return activities_str
   