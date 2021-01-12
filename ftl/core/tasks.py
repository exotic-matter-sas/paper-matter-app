#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
import logging

from celery import shared_task
from django.conf import settings
from django.core import management
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone, translation

from core.models import FTLOrg, FTLDocument, FTLFolder, FTLDocumentReminder
from core.processing.ftl_processing import FTLDocumentProcessing

logger = logging.getLogger(__name__)


@shared_task
def apply_ftl_processing(ftl_doc_pid, org_id, user_id, force):
    doc = FTLDocument.objects.get(pid=ftl_doc_pid, org_id=org_id, ftl_user_id=user_id)
    ftl_document_processing = FTLDocumentProcessing()
    ftl_document_processing.apply_processing(doc, force)


@shared_task
def delete_document(ftl_doc_pid, org_id, user_id):
    try:
        doc = FTLDocument.objects.get(
            pid=ftl_doc_pid, org_id=org_id, ftl_user_id=user_id
        )
        doc.delete()
    except FTLDocument.DoesNotExist:
        pass


@shared_task
def send_email_async(*args, **kwargs):
    send_mail(*args, **kwargs)


####################
# TASKS USED IN CRON
####################


@shared_task
def batch_delete_org():
    orgs_to_delete = FTLOrg.objects.filter(deleted=True)

    for org in orgs_to_delete:
        docs = FTLDocument.objects.filter(org=org).exists()
        folders = FTLFolder.objects.filter(org=org).exists()

        if docs or folders:
            logger.info(f"Skipping {org}")
        else:
            logger.info(f"Deleting {org} ...")
            org.delete()


@shared_task
def batch_delete_doc():
    docs_to_delete = FTLDocument.objects.filter(deleted=True)

    for doc in docs_to_delete:
        logger.info(f"Deleting {doc.pid} ...")
        doc.delete()


@shared_task
def batch_delete_oauth_tokens():
    management.call_command("cleartokens")


@shared_task
def batch_documents_reminder():
    instance_host = getattr(settings, "FTL_EXTERNAL_HOST", "")
    now_in_utc = timezone.now()
    reminders = FTLDocumentReminder.objects.filter(alert_on__lte=now_in_utc).order_by(
        "ftl_user_id"
    )

    for reminder in reminders:
        logger.info(
            f"Sending reminder email for {reminder.ftl_doc.pid} ({reminder.alert_on})"
        )

        # We manually build the URL because we don't have any request or named url for document
        doc_url = f"{instance_host}/app/#/home?doc={reminder.ftl_doc.pid}"

        ctx = {
            "title": reminder.ftl_doc.title,
            "note": reminder.note,
            "alert_on": reminder.alert_on,
            "doc_url": doc_url,
        }

        # Force user lang setting for email
        with translation.override(reminder.ftl_user.lang or "en"):
            subject_reminder = render_to_string(
                template_name="core/email/core_email_reminder_subject.txt", context=ctx,
            )
            subject_reminder = "".join(subject_reminder.splitlines())
            message_reminder = render_to_string(
                template_name="core/email/core_email_reminder_body.txt", context=ctx
            )

        # Email sent to the current user email for notification
        reminder.ftl_user.email_user(
            subject_reminder, message_reminder, settings.DEFAULT_FROM_EMAIL
        )

        reminder.delete()
