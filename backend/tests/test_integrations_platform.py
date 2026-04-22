import unittest

from app.services.integrations import PROVIDER_REGISTRY, list_provider_definitions


class IntegrationPlatformTests(unittest.TestCase):
    def test_provider_catalog_includes_manual_stripe_connector(self):
        providers = {provider["key"]: provider for provider in list_provider_definitions()}
        self.assertIn("stripe", providers)
        self.assertEqual(providers["stripe"]["connection_mode"], "manual")
        self.assertFalse(providers["stripe"]["oauth_supported"])

    def test_stripe_connector_rejects_non_secret_keys(self):
        stripe_provider = PROVIDER_REGISTRY["stripe"]
        with self.assertRaises(Exception) as ctx:
            stripe_provider.validate_credentials({"api_key": "pk_live_public"})
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
