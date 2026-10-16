# CRM Lead Capture — Integration Reference

How leads from any website reach the KCGlobed CRM, and how the CRM decides which
**Source** every lead belongs to. Use this document to connect a new website or to
understand the existing gcc_backend → CRM integration.

---

## 1. The endpoint

```
POST https://crm-backend.kcglobed.com/api/v1/leads/capture
Content-Type: application/json
x-api-key: <CAPTURE_API_KEY>
```

> **Call this from your website's server, never from browser JavaScript.**
> The API key would be visible in the page source. Pattern: visitor form → your backend → CRM.

- `201` — success, for both a new lead and a duplicate (see §6)
- `401` — wrong/missing API key
- `400` — field-wise validation errors in the response body

## 2. Minimum payload

Only two things are truly required. Everything else improves tracking and profile quality.

```json
{
  "name": "Rahul Sharma",
  "mobile": "9876543210"
}
```

- `name` — ya `firstName` + `lastName` alag-alag
- `mobile` — 10 digits, 6–9 se start; `+91` / leading `0` khud strip ho jata hai

## 3. Full field reference

| Field | Required | What it does |
|---|---|---|
| `name` | yes* | Full name; split into first/last automatically. Or send `firstName` + `lastName`. |
| `mobile` | yes | Lead identity. Duplicate detection runs on this (and email). |
| `email` | no | Also used for duplicate detection. |
| `city` / `state` | no | Stored on the lead. |
| `program` | no | Matched to a Program master by name or code (e.g. `"GMBA"`). |
| `utm_source` | tracking | **Drives the Source** when no explicit `source` is sent — see §4. |
| `utm_medium` `utm_campaign` `utm_term` `utm_content` | tracking | Stored in the lead's UTM block; visible on the lead detail page and filterable. |
| `landing_page` | tracking | Which page the form was on (path or full URL). |
| `referrer` | tracking | `document.referrer`. **Send it even when empty** — empty string means the visitor came directly (typed the URL), which classifies the lead as *Direct*. |
| `source` | optional | Explicit Source name. **Overrides the UTM logic** — lead files under exactly this Source (auto-created if new). Use for partners and named integrations. |
| `referral_code` `partner_name` `partner_link` | partner | Partner attribution, stored in the lead's referral block (example F). |
| `track` | optional | `ads` \| `partner` \| `other` — lead category. |

## 4. How the CRM decides the Source

The decision runs top-down — **the first rule that matches wins**:

1. **Explicit `source` in the payload** → lead files under exactly that Source master
   (auto-created if it doesn't exist). Use for partners or when a whole website should
   be its own source.

2. **`utm_source` is a known value** → mapped to a standard Source:

   | utm_source | Source | Channel |
   |---|---|---|
   | `facebook` `fb` `instagram` `meta` | Meta Ads | Paid Ads |
   | `google` `adwords` | Google Ads | Paid Ads |
   | `linkedin` | LinkedIn | Paid Ads |
   | `whatsapp` `sms` `email` `outreach` | WhatsApp / SMS / Email / Outreach | Referral |
   | `webinar` `seminar` `event` | Webinar / Seminar / Event | Events |

3. **`utm_source` is some other value** → lead files under **"Other"**.
   The raw utm value still shows in the lead's UTM block, so campaign reporting survives.

4. **No UTM at all** → the `referrer` decides:
   - empty string `""` → **Direct** (visitor typed the URL)
   - anything else, or referrer not sent → **Website** (organic)

### First Source vs Latest Source

- **First Source** — set once, on the lead's first capture, never changes. Use for
  "who brought this student".
- **Latest Source** — updates whenever the same person enquires again from somewhere else.
- A lead's **channel** (Paid Ads / Organic / Partner / Direct …) is a property of its
  Source in Masters → Sources. Move a Source to another channel and all its leads report
  under the new channel.

## 5. Ready payloads, scenario-wise

### A — Facebook / Instagram ad lead → Source: Meta Ads

```json
{
  "name": "Rahul Sharma", "mobile": "9876543210", "email": "rahul@gmail.com",
  "city": "Jaipur", "state": "Rajasthan",
  "utm_source": "facebook", "utm_medium": "cpc", "utm_campaign": "oct-intake",
  "landing_page": "https://gccschool.com/apply", "referrer": "https://l.facebook.com/"
}
```

### B — Google ad lead → Source: Google Ads

```json
{
  "name": "Priya Verma", "mobile": "9812345678",
  "utm_source": "google", "utm_medium": "cpc", "utm_campaign": "brand-search",
  "landing_page": "/apply", "referrer": "https://www.google.com/"
}
```

### C — Visitor typed the URL directly → Source: Direct

```json
{
  "name": "Aman Gupta", "mobile": "9700011122",
  "landing_page": "/index.html", "referrer": ""
}
```

Note: `referrer` khaali string bhejna zaroori hai — yahi Direct ka signal hai.

### D — Came via another site / organic → Source: Website

```json
{
  "name": "Neha Jain", "mobile": "9600022233",
  "landing_page": "/programs/gmba", "referrer": "https://www.bing.com/"
}
```

### E — New website / named integration → its own Source

Explicit `source` overrides everything — the whole site reports under one name.
UTM phir bhi store hota hai.

```json
{
  "name": "Vikas Yadav", "mobile": "9500033344",
  "source": "AEUAP Hiring Drive",
  "utm_source": "facebook", "utm_campaign": "aeuap-oct",
  "landing_page": "https://drive.gccschool.com/", "referrer": ""
}
```

> A brand-new Source auto-creates. For clean reporting, **pre-create the Source in
> Masters → Sources** with the channel you want (e.g. Partner) — capture then reuses it.

### F — Channel-partner lead → Source: partner's name + referral block

```json
{
  "name": "Sunita Rao", "mobile": "9400044455",
  "source": "EduBridge Consultants", "track": "partner",
  "referral_code": "CP-204",
  "partner_name": "EduBridge Consultants",
  "partner_link": "https://gccschool.com/apply?referral_code=CP-204"
}
```

## 6. Duplicates & re-enquiry

If the mobile (or email) already belongs to a live lead, the CRM does **not** create a
second lead. It records a **re-enquiry** on the existing one:

- empty fields get filled
- **Latest Source updates** to the new origin, **First Source stays**
- the counsellor is notified; a closed lead reopens
- response is still `201` with `"duplicate": true`

Sending the same person twice is always safe.

## 7. What the CRM does after capture

**Immediately:** lead number issued (`GCCSCH-…`) · stage **Untouched** · Source + UTM +
referral stored · round-robin assigns an online counsellor (or the lead pools until one
logs in) · assignment notification goes out.

**Visible where:** Leads list columns & filters (Latest/First Source, Channel, UTM) ·
lead detail's UTM block · timeline entry "Lead created via …" · exports.

## 8. Response shape

```json
{
  "success": true, "status": 201,
  "message": "Lead captured successfully",
  "data": {
    "duplicate": false,
    "lead": { "leadNo": "GCCSCH-2026-0101742", "source": {}, "utm": {}, "stage": {}, "owner": {} }
  }
}
```

(For a re-enquiry: `"message": "Existing lead updated with re-enquiry"`, `"duplicate": true`.)

## 9. New-website checklist

1. Get the `CAPTURE_API_KEY`; keep it on your server only.
2. On the landing page, capture UTM params from the URL and `document.referrer`
   (snippet below), pass them to your backend with the form.
3. Decide the source strategy:
   - **UTM-driven** — send no `source`; ads classify themselves via §4
   - **Named** — send `source` for the whole site / per partner
4. Always send `referrer`, even when it is `""`.
5. Test one submit per scenario you use, then open the lead in the CRM: check Source,
   the UTM block, and the timeline's "created" entry.

### Landing-page snippet — collect tracking for the form post

```js
const q = new URLSearchParams(location.search);
const tracking = {
  utm_source:   q.get('utm_source')   || '',
  utm_medium:   q.get('utm_medium')   || '',
  utm_campaign: q.get('utm_campaign') || '',
  utm_term:     q.get('utm_term')     || '',
  utm_content:  q.get('utm_content')  || '',
  landing_page: location.href,
  referrer:     document.referrer        // '' bhi bhejo — Direct ka signal hai
};
```

---

## 10. Where this lives in gcc_backend

The gcc_backend already implements this integration. Entry points:

| File | What it does |
|---|---|
| `utils/crm_connect.py` | `send_lead_to_crm(full_name, phone, email, city, state, *, source=None, program=None, utm=None, landing_page=None, referrer=None)` — the capture call. Strips blank fields **except `referrer`** (empty string is the Direct signal). Gated on `CRM_STATUS == 'True'`. Also `crm_program()`: gcc program choice → CRM Program master name (**1 CPA → AEUAP, 2 EA → AEUTP, 3 ACCA → AEIAP**). |
| `career/serializers.py` | `CreateDossierDataSerializer.create` and `CreateDossierDataCustomAffliateSerializer.create` call `send_lead_to_crm` with the form's UTM data and `program=crm_program(instance.program)`. **No explicit `source` is sent** — by design, the CRM derives it from `utm_source` (§4 rules 2–4). |
| `students/crm_sync.py` | Profile sync hub: `sync_profile_async` pushes draft (partial) / final profiles to the CRM profile-capture API; `fetch_or_create_lead_no` gives new signups their CRM lead number as `application_id`; `fetch_crm_profile` + `crm_overrides` read CRM edits back onto the website profile. |
| `users/serializers.py` | `create_student` — signup uses `fetch_or_create_lead_no` so `application_id` = CRM lead number. |

### Environment variables (gcc_backend `.env`)

| Variable | Purpose |
|---|---|
| `CRM_STATUS` | `True` enables the CRM hooks |
| `CRM_CAPTURE_URL` | Base URL of the CRM public API |
| `CRM_CAPTURE_KEY` | `x-api-key` for capture / profile-capture (write) |
| `CRM_READ_KEY` | `x-api-key` for profile-fetch (read overlay) |

---

*Source priority ek line me: explicit `source` → utm map → "Other" → Direct ("" referrer) / Website.*
