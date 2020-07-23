#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
from unittest.mock import Mock

from django.test import override_settings, TestCase
from django.urls import reverse_lazy


@override_settings(FTL_ADMIN_ENABLE_IP_PROTECTION=True)
@override_settings(FTL_ADMIN_IP_RANGE_ALLOWED=["127.0.0.1/32", "10.0.0.0/8"])
class TestFTLAdminIPFilter(TestCase):
    def setUp(self):
        self.get_response_mock = Mock()

    def test_is_not_blocked_1(self):
        response = self.client.get(reverse_lazy("admin:login"), REMOTE_ADDR="127.0.0.1")
        self.assertEqual(response.status_code, 200)

    def test_is_not_blocked_2(self):
        response = self.client.get(
            reverse_lazy("admin:login"), REMOTE_ADDR="10.42.0.10"
        )
        self.assertEqual(response.status_code, 200)

    def test_is_blocked(self):
        response = self.client.get(reverse_lazy("admin:login"), REMOTE_ADDR="128.0.0.1")
        self.assertEqual(response.status_code, 404)

    def test_not_blocking_other_app(self):
        response = self.client.get(
            reverse_lazy("home"), follow=True, REMOTE_ADDR="127.0.0.1"
        )
        self.assertEqual(response.status_code, 200)


@override_settings(FTL_ADMIN_ENABLE_IP_PROTECTION=True)
@override_settings(FTL_ADMIN_IP_RANGE_ALLOWED=["127.0.0.1/32", "10.0.0.0/8"])
@override_settings(FTL_ADMIN_IP_PROXY_COUNT=1)
@override_settings(
    FTL_ADMIN_IP_META_PRECEDENCE_ORDER=["HTTP_X_FORWARDED_FOR", "X_FORWARDED_FOR",]
)
class TestFTLAdminIPFilterForwardHeader(TestCase):
    def test_ip_header_forwarding_with_lb_not_blocked(self):
        response = self.client.get(
            reverse_lazy("admin:login"), HTTP_X_FORWARDED_FOR="127.0.0.1, 190.0.0.1"
        )
        self.assertEqual(response.status_code, 200)

    def test_ip_header_forwarding_with_lb_blocked(self):
        response = self.client.get(
            reverse_lazy("admin:login"), HTTP_X_FORWARDED_FOR="128.0.0.1, 190.0.0.1"
        )
        self.assertEqual(response.status_code, 404)
