#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for license information.
from django.test import TestCase, override_settings
from django.urls import reverse


class FTLCSPHeaderTests(TestCase):
    @override_settings(CSP_REPORT_ONLY=True)
    def test_csp_header_report_only(self):
        response = self.client.get(reverse("login"))
        self.assertIn("Content-Security-Policy-Report-Only", response)

    @override_settings(CSP_REPORT_ONLY=False)
    def test_csp_header_report(self):
        response = self.client.get(reverse("login"))
        self.assertIn("Content-Security-Policy", response)

    @override_settings(CSP_REPORT_ONLY=False)
    def test_csp_header_content(self):
        response = self.client.get(reverse("login"))
        csp_header_elems = (
            c.strip() for c in response["Content-Security-Policy"].split(";")
        )

        self.assertTrue(
            (s for s in csp_header_elems if "connect-src 'self' blob:" in s)
        )
        self.assertTrue((s for s in csp_header_elems if "img-src 'self' data:" in s))
        self.assertTrue((s for s in csp_header_elems if "frame-src 'self'" in s))
        self.assertTrue((s for s in csp_header_elems if "default-src 'self'" in s))
        self.assertTrue((s for s in csp_header_elems if "script-src 'self'" in s))
        self.assertTrue((s for s in csp_header_elems if "style-src 'self'" in s))
        self.assertTrue((s for s in csp_header_elems if "nonce-" in s))
