import requests
from django.conf import settings


def send_lead_to_crm(full_name, phone, email=None, city=None, state=None):
    """
    Pushes one lead to the CRM. Returns (ok, data).
    Duplicate mobile/email par CRM khud re-enquiry handle karta hai.
    """
    payload = {
        'name': full_name,
        'mobile': phone,
        'email': email,
        'city': city,
        'state': state,
    }
    # khali fields mat bhejo
    payload = {k: v for k, v in payload.items() if v}

    try:
        response = requests.post(
            settings.CRM_CAPTURE_URL,
            json=payload,
            headers={'x-api-key': settings.CRM_CAPTURE_KEY},
            timeout=10,
        )
    except requests.RequestException as exc:
        return False, {'error': str(exc)}
    print("response...",response)
    print("response code...",response.status_code)
    if response.status_code == 201:
        data = response.json()['data']
        return True, data

    return False, response.json() if response.content else {}