import logging

import requests
from django.conf import settings

log = logging.getLogger('crm_sync')


def send_lead_to_crm(full_name, phone, email=None, city=None, state=None, *,
                     source=None, utm=None, landing_page=None, referrer=None):
    """
    Pushes one lead to the CRM capture API — tracking ke saath:
      source        -> CRM Source master ka naam (naya ho to auto-create)
      utm           -> {'source','medium','campaign','term','content'} jo bhare hon
      landing_page  -> kis page se form bhara (CRM lead ke utm.landingPage me)
      referrer      -> document.referrer; KHAALI string bhi bhejo — CRM uske
                       'Direct' classification ke liye use karta hai
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
        'landing_page': landing_page,
    }
    for key, value in (utm or {}).items():
        payload[f'utm_{key}'] = value
    # khali fields mat bhejo…
    payload = {k: v for k, v in payload.items() if v}
    # …siwaye referrer ke: '' ka matlab hai "seedha aaya" (Direct), wo bhi signal hai
    if referrer is not None:
        payload['referrer'] = referrer

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
