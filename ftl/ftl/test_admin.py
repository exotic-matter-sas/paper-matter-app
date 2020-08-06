#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from django.test import TestCase
from django.urls import reverse

from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_authenticated_session,
)


class AdminLoginFTLTests(TestCase):
    def setUp(self):
        self.org = setup_org()
        self.admin = setup_admin(org=self.org)
        self.org_1 = setup_org(name=tv.ORG_NAME_2, slug=tv.ORG_SLUG_2)
        self.user_1 = setup_user(self.org_1)

    def test_admin_user_already_logged(self):
        setup_authenticated_session(self.client, self.org, self.admin)
        response = self.client.get(reverse("admin:index"), follow=True)
        self.assertContains(response, "Welcome")

    def test_non_admin_user_already_logged(self):
        setup_authenticated_session(self.client, self.org_1, self.user_1)
        response = self.client.get(reverse("admin:login"), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_not_logged(self):
        response = self.client.get(reverse("admin:index"), follow=True)
        self.assertRedirects(response, f"{reverse('login')}?next=/admin/")
