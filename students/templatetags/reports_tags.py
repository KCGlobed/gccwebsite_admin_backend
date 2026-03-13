from django import template
from users.models import *
import math
register = template.Library()
from datetime import datetime, date


@register.filter("convert_comma_format")
def convert_comma_format(activities):
    activities_str = ", ".join(map(str, activities)) if isinstance(activities, list) else str(activities)
    
    return activities_str
   