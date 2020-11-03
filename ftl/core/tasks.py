#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import logging

from celery import shared_task
from django.core import management
from django.core.mail import send_mail

from core.models import FTLOrg, FTLDocument, FTLFolder
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
