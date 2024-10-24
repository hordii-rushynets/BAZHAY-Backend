from django.conf import settings
from appstoreserverlibrary.models.Environment import Environment
from appstoreserverlibrary.signed_data_verifier import VerificationException, SignedDataVerifier


class ApplePayment:
    def __init__(self):
        self.app_apple_id = settings.APPLE_KEY_ID
        self.issuer_id = settings.APPLE_ISSUER_ID
        self.bundle_id = settings.APPLE_BUNDLE_ID
        self.environment = settings.APPLE_ENVIRONMENT

    def load_root_certificates(self, file_path):
        with open(file_path, "rb") as f:
            root_certificates = f.read()
        return root_certificates

    def decryption(self, signed_notification):
        root_certificates = self.load_root_certificates('premium/AuthKey_F74XYY2WSM.p8')
        try:
            signed_data_verifier = SignedDataVerifier(
                root_certificates=self.root_certificates,
                enable_online_checks=True,
                environment=self.environment,
                bundle_id=self.bundle_id,
                app_apple_id=self.app_apple_id
            )

            payload = signed_data_verifier.verify_and_decode_notification(signed_notification)
            return payload

        except VerificationException as e:
            print(f"Verification error: {e}")
            return None

