#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
import datetime
from unittest.mock import patch, call, ANY

import pytz
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from core.models import FTLDocument, FTLOrg, FTLDocumentReminder
from core.tasks import batch_delete_doc, batch_delete_org, batch_documents_reminder
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_document,
    setup_folder,
    setup_temporary_file,
)
from ftl import celery


class RecurringTasksTests(APITestCase):
    def setUp(self):
        self.org_with_docs = setup_org()
        setup_admin(self.org_with_docs)
        self.user = setup_user(self.org_with_docs)

        self.doc = setup_document(self.org_with_docs, self.user)
        self.doc_bis = setup_document(
            self.org_with_docs, self.user, title=tv.DOCUMENT2_TITLE
        )

        self.first_level_folder = setup_folder(
            self.org_with_docs, name="First level folder"
        )

        self.doc_in_folder = setup_document(
            self.org_with_docs,
            self.user,
            title="Document in folder",
            ftl_folder=self.first_level_folder,
        )

        self.org_with_folders = setup_org(name=tv.ORG_NAME_2, slug=tv.ORG_SLUG_2)
        setup_folder(self.org_with_folders)

        self.org_without_docs_1 = setup_org(name=tv.ORG_NAME_3, slug=tv.ORG_SLUG_3)
        self.org_without_docs_2 = setup_org(name=tv.ORG_NAME_4, slug=tv.ORG_SLUG_4)

    def test_batch_delete_document(self):
        binary_f = setup_temporary_file().name
        ftl_document = FTLDocument.objects.create(
            org=self.org_with_docs,
            ftl_user=self.user,
            title="Test document to be deleted",
            binary=binary_f,  # We don't want to delete the test pdf file
        )
        self.assertIsNotNone(ftl_document.pid)
        initial_doc_count = FTLDocument.objects.count()

        ftl_document.deleted = True
        ftl_document.save()

        batch_delete_doc()

        with self.assertRaises(FTLDocument.DoesNotExist):
            FTLDocument.objects.get(pid=ftl_document.pid)

        self.assertEqual(
            FTLDocument.objects.count(),
            initial_doc_count - 1,
            "Only one doc should have been deleted",
        )

    def test_batch_delete_org(self):
        # given
        # org_with_docs marked as deleted
        # org_with_folders marked as deleted
        # org_without_docs_1 not marked as deleted
        # org_without_docs_2 marked as deleted
        self.org_with_docs.deleted = True
        self.org_with_docs.save()
        self.org_with_folders.deleted = True
        self.org_with_folders.save()
        self.org_without_docs_2.deleted = True
        self.org_without_docs_2.save()

        # when
        batch_delete_org()

        # then, only orgs marked as deleted AND with no docs or folders left are deleted
        self.assertTrue(FTLOrg.objects.filter(pk=self.org_with_docs.pk).exists())
        self.assertTrue(FTLOrg.objects.filter(pk=self.org_with_folders.pk).exists())
        self.assertTrue(FTLOrg.objects.filter(pk=self.org_without_docs_1.pk).exists())
        self.assertFalse(FTLOrg.objects.filter(pk=self.org_without_docs_2.pk).exists())

    @patch("core.tasks.render_to_string")
    @patch.object(celery.app, "send_task")
    @override_settings(FTL_EXTERNAL_HOST="http://example-pm.org")
    def test_batch_alert_documents(self, mocked_email_send, mocked_render_to_string):
        now_minus_1_day_utc = timezone.now() + datetime.timedelta(days=-1)
        now_plus_1_day_utc = timezone.now() + datetime.timedelta(days=1)
        now_plus_1_week_utc = timezone.now() + datetime.timedelta(weeks=1)
        now_plus_1_month_utc = timezone.now() + datetime.timedelta(weeks=4)

        alert_db_minus_1_day = FTLDocumentReminder()
        alert_db_minus_1_day.ftl_doc = self.doc
        alert_db_minus_1_day.ftl_user = self.user
        alert_db_minus_1_day.alert_on = now_minus_1_day_utc
        alert_db_minus_1_day.save()

        alert_db_plus_1_day = FTLDocumentReminder()
        alert_db_plus_1_day.ftl_doc = self.doc
        alert_db_plus_1_day.ftl_user = self.user
        alert_db_plus_1_day.alert_on = now_plus_1_day_utc
        alert_db_plus_1_day.save()

        alert_db_plus_1_week = FTLDocumentReminder()
        alert_db_plus_1_week.ftl_doc = self.doc
        alert_db_plus_1_week.ftl_user = self.user
        alert_db_plus_1_week.alert_on = now_plus_1_week_utc
        alert_db_plus_1_week.save()

        alert_db_plus_1_month = FTLDocumentReminder()
        alert_db_plus_1_month.ftl_doc = self.doc
        alert_db_plus_1_month.ftl_user = self.user
        alert_db_plus_1_month.alert_on = now_plus_1_month_utc
        alert_db_plus_1_month.save()

        # Time is now
        with patch.object(timezone, "now") as mocked_timezone_now:
            mocked_timezone_now.return_value = datetime.datetime.utcnow().replace(
                tzinfo=pytz.utc
            )
            batch_documents_reminder()

        # Expired alert is removed
        with self.assertRaises(FTLDocumentReminder.DoesNotExist):
            alert_db_minus_1_day.refresh_from_db()

        # Time is moved forward, hours per hours
        with patch.object(timezone, "now") as mocked_timezone_now:
            moving_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            mocked_timezone_now.return_value = moving_datetime

            # Forward until next month
            while moving_datetime < now_plus_1_month_utc:
                moving_datetime = moving_datetime + datetime.timedelta(hours=1)
                mocked_timezone_now.return_value = moving_datetime
                batch_documents_reminder()

        # Three emails should have been sent
        self.assertEqual(mocked_email_send.call_count, 3)

        # render_to_string should have been called 2*3 times
        self.assertListEqual(
            mocked_render_to_string.call_args_list,
            [
                call(
                    template_name=ANY,
                    context={
                        "title": self.doc.title,
                        "note": "",
                        "alert_on": alert_db_plus_1_day.alert_on,
                        "doc_url": f"http://example-pm.org/app/#/home?doc={self.doc.pid}",
                    },
                ),
                call(
                    template_name=ANY,
                    context={
                        "title": self.doc.title,
                        "note": "",
                        "alert_on": alert_db_plus_1_day.alert_on,
                        "doc_url": f"http://example-pm.org/app/#/home?doc={self.doc.pid}",
                    },
                ),
                call(
                    template_name=ANY,
                    context={
                        "title": self.doc.title,
                        "note": "",
                        "alert_on": alert_db_plus_1_week.alert_on,
                        "doc_url": f"http://example-pm.org/app/#/home?doc={self.doc.pid}",
                    },
                ),
                call(
                    template_name=ANY,
                    context={
                        "title": self.doc.title,
                        "note": "",
                        "alert_on": alert_db_plus_1_week.alert_on,
                        "doc_url": f"http://example-pm.org/app/#/home?doc={self.doc.pid}",
                    },
                ),
                call(
                    template_name=ANY,
                    context={
                        "title": self.doc.title,
                        "note": "",
                        "alert_on": alert_db_plus_1_month.alert_on,
                        "doc_url": f"http://example-pm.org/app/#/home?doc={self.doc.pid}",
                    },
                ),
                call(
                    template_name=ANY,
                    context={
                        "title": self.doc.title,
                        "note": "",
                        "alert_on": alert_db_plus_1_month.alert_on,
                        "doc_url": f"http://example-pm.org/app/#/home?doc={self.doc.pid}",
                    },
                ),
            ],
        )

        # All reminders have been sent and so removed from DB
        with self.assertRaises(FTLDocumentReminder.DoesNotExist):
            alert_db_plus_1_day.refresh_from_db()
        with self.assertRaises(FTLDocumentReminder.DoesNotExist):
            alert_db_plus_1_week.refresh_from_db()
        with self.assertRaises(FTLDocumentReminder.DoesNotExist):
            alert_db_plus_1_month.refresh_from_db()
