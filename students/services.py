import hashlib
import base64
import requests
from collections import OrderedDict
from datetime import datetime, timedelta


class CoCubesAssessmentService:

    BASE_URL = "https://www.cocubes.com/partner-assessment/sassl"

    # Provided by CoCubes
    HASH_SALT = "e3eb8a07fa96e6f0"

    # POT = 67119112
    OOT = 67119112
    # PASS_KEY = "211327"
    # PASS_KEY = 904082
    PASS_KEY = 115143
    ##
    @classmethod
    def generate_ticks(cls, minutes=30):
        """
        Generate .NET ticks
        """
        future_time = datetime.utcnow() + timedelta(minutes=minutes)

        ticks = int(
            (future_time - datetime(1, 1, 1)).total_seconds() * 10**7
        )

        return str(ticks)

    @classmethod
    def generate_hash(cls, params):
        """
        Generate hk value
        """

        sorted_params = OrderedDict(sorted(params.items()))

        values = list(sorted_params.values())
        # print(values)
        hash_string = (
            cls.HASH_SALT
            + cls.HASH_SALT.join(values)
            + cls.HASH_SALT
        )
        # print(hash_string)
        sha1_hash = hashlib.sha1(
            hash_string.encode("utf-8")
        ).digest()

        hk = base64.b64encode(sha1_hash).decode()

        hk = hk.replace("+", "-").replace("/", "_").replace("=", ",")

        return hk

    @classmethod
    def schedule_assessment(cls,email, first_name, last_name="", test_expiry_days=1, redirect_url=None, pass_keys=""):

        expires = cls.generate_ticks()
        print("expire..", expires)
        payload = {
            "servicename": "sassl",
            "v": "4",
            "email": email,
            "name": f"{first_name}+{last_name}",
            # "pot": cls.POT,
            "oot": str(cls.OOT),
            "expires": str(expires),
            "testexpirydays": str(test_expiry_days),
            "getsignonurl": "1",
            "pk": str(pass_keys)
        }
        if redirect_url:
            payload["rurl"] = redirect_url
        print("paylo", payload)

        # Generate hash key
        # print("hhh", cls.generate_hash(payload))
        payload["hk"] = cls.generate_hash(payload)

        print("payload.....",payload)

        response = requests.get(
            cls.BASE_URL,
            params=payload,
            timeout=30
        )
        print(response.json)
        print(response.text)
        return response.json()