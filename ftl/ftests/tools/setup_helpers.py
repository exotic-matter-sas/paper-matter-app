from core.models import FTLOrg, FTLUser, FTLDocument, FTLFolder, permissions_names_to_objects, FTL_PERMISSIONS_USER
from core.views import SEARCH_VECTOR
from ftests.tools import test_values as tv


def setup_org(name=tv.ORG_NAME_1, slug=tv.ORG_SLUG_1):
    return FTLOrg.objects.create(
        name=name,
        slug=slug,
    )


def setup_admin(org, email=tv.ADMIN_EMAIL, username=tv.ADMIN_USERNAME, password=tv.ADMIN_PASS):
    return FTLUser.objects.create_superuser(
        org=org,
        email=email,
        username=username,
        password=password,
    )


def setup_user(org, email=tv.USER1_EMAIL, username=tv.USER1_USERNAME, password=tv.USER1_PASS):
    user = FTLUser.objects.create_user(org=org, email=email, username=username, password=password, )
    user.user_permissions.set(permissions_names_to_objects(FTL_PERMISSIONS_USER))
    return user


def setup_authenticated_session(test_client, org, user):
    session = test_client.session
    session.update({
        'org_name': org.name,
        'org_id': org.id,
    })
    session.save()
    test_client.force_login(user)


def setup_document(org, ftl_user, ftl_folder=None, title=tv.DOCUMENT1_TITLE, note=tv.DOCUMENT1_NOTE,
                   binary=tv.DOCUMENT1_BINARY_PATH, text_content=tv.DOCUMENT1_CONTENT, language=tv.DOCUMENT1_LANGUAGE):
    document = FTLDocument.objects.create(
        org=org,
        ftl_user=ftl_user,
        ftl_folder=ftl_folder,
        title=title,
        note=note,
        binary=binary,
        content_text=text_content,
        language=language,
    )
    # Update document to allow PGSQL to process search vector
    document.tsvector = SEARCH_VECTOR
    document.save()

    return document


def setup_folder(org, name=tv.FOLDER1_NAME, parent=None):
    return FTLFolder.objects.create(
        org=org,
        name=name,
        parent=parent,
    )
