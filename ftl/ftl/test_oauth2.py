#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import json
from urllib.parse import urlparse, parse_qs

from django.test import TestCase
from oauth2_provider.models import Application
from rest_framework.reverse import reverse

from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_authenticated_session,
)


class OAuth2FTLTests(TestCase):
    def setUp(self):
        self.org = setup_org()
        self.admin = setup_admin(org=self.org)
        self.application = Application.objects.create(
            name="Test Application",
            redirect_uris=("http://localhost:1123"),
            user=self.admin,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            skip_authorization=False,
        )

    def test_oauth2_authorization_code_flow(self):
        setup_authenticated_session(self.client, self.org, self.admin)

        # Third party app open user browser to the following URL (user is already logged)
        response = self.client.get(
            reverse("authorize"),
            {
                "client_id": self.application.client_id,
                "response_type": "code",
                "state": "random_state_string",
                "scope": "read write",
                "redirect_uri": "http://localhost:1123",
            },
        )
        self.assertEqual(response.status_code, 200)

        # User authorize app by clicking on the submit button
        form_data = {
            "client_id": self.application.client_id,
            "state": "random_state_string",
            "scope": "read write",
            "redirect_uri": "http://localhost:1123",
            "response_type": "code",
            "allow": True,
        }
        response_authorize = self.client.post(reverse("authorize"), data=form_data)

        # Verify we have the redirect to the localhost server
        self.assertEqual(response_authorize.status_code, 302)

        url_parsed = urlparse(response_authorize["Location"])
        query_parsed = parse_qs(url_parsed.query)

        self.assertIn("http://localhost:1123", response_authorize["Location"])
        self.assertEqual("random_state_string", query_parsed["state"][0])
        self.assertIsNotNone(query_parsed["code"][0])

        # Use authorization code to get a token
        post = {
            "client_id": self.application.client_id,
            "client_secret": self.application.client_secret,
            "grant_type": "authorization_code",
            "code": query_parsed["code"][0],
            "redirect_uri": "http://localhost:1123",
        }
        response_token = self.client.post(reverse("token"), data=post)
        self.assertEqual(response_token.status_code, 200)

        # Use token with API
        content = json.loads(response_token.content.decode("utf-8"))
        response_documents = self.client.get(
            "/app/api/v1/documents",
            format="json",
            Authorization=f"Bearer {content['access_token']}",
        )
        self.assertEqual(response_documents.status_code, 200)
        self.assertGreaterEqual(response_documents.data["count"], 0)
