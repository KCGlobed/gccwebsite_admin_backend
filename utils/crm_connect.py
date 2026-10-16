import logging

import requests
from django.conf import settings

log = logging.getLogger('crm_sync')

# gcc ProgramType (career.models) -> CRM Program master ka naam:
# CPA = US Accounting -> AEUAP, EA = US Taxation -> AEUTP, ACCA -> AEIAP
GCC_PROGRAM_TO_CRM = {1: 'AEUAP', 2: 'AEUTP', 3: 'AEIAP'}


def crm_program(program_id):
    """gcc ka program choice (1=CPA/2=EA/3=ACCA) -> CRM Program master ka naam, warna None."""
    return GCC_PROGRAM_TO_CRM.get(program_id)


def send_lead_to_crm(full_name, phone, email=None, city=None, state=None, *,
                     source=None, program=None, utm=None, landing_page=None, referrer=None,
                     custom=None):
    """
    Pushes one lead to the CRM capture API — tracking ke saath:
      source        -> CRM Source master ka naam (naya ho to auto-create)
      program       -> CRM Program master ka naam ya code (gcc choice ke liye crm_program() use karo)
      utm           -> {'source','medium','campaign','term','content'} jo bhare hon
      landing_page  -> kis page se form bhara (CRM lead ke utm.landingPage me)
      referrer      -> document.referrer; sirf tracking ke liye store hota hai,
                       Source pe asar nahi karta (Direct classification hat chuki hai)
      custom        -> {'Label': value} extra form data; CRM me custom field ban kar
                       lead ke Additional Lead Information card pe dikhta hai
                       (naya label CRM me text custom-field auto-create karta hai)
    Duplicate mobile/email par CRM khud re-enquiry handle karta hai.
    Returns (ok, data).
    """
    payload = {
        'name': full_name,
        'mobile': phone,
        'email': email,
        'city': city,
        'state': state,
        'source': source,
        'program': program,
        'landing_page': landing_page,
    }
    for key, value in (utm or {}).items():
        payload[f'utm_{key}'] = value
    # khali fields mat bhejo; referrer bhara ho to tracking ke liye saath jaye
    payload = {k: v for k, v in payload.items() if v}
    if referrer:
        payload['referrer'] = referrer
    custom = {k: v for k, v in (custom or {}).items() if v not in (None, '')}
    if custom:
        payload['custom_fields'] = custom

    try:
        response = requests.post(
            settings.CRM_CAPTURE_URL,
            json=payload,
            headers={'x-api-key': settings.CRM_CAPTURE_KEY},
            timeout=5,  # student ka form kabhi CRM ke bharose atke nahi
        )
    except requests.RequestException as exc:
        log.warning('CRM capture failed for %s: %s', phone, exc)
        return False, {'error': str(exc)}
    if response.status_code == 201:
        return True, response.json()['data']
    log.warning('CRM capture rejected for %s: %s %s', phone, response.status_code, response.text[:200])
    return False, response.json() if response.content else {}
