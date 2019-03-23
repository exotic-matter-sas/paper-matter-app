from django.contrib import admin
# Register your models here.
from django.contrib.auth.admin import UserAdmin
from mptt.admin import MPTTModelAdmin

from core.models import FTLOrg, FTLUser, FTLDocument, FTLFolder

admin.site.register(FTLOrg)
admin.site.register(FTLUser, UserAdmin)
admin.site.register(FTLDocument)
admin.site.register(FTLFolder, MPTTModelAdmin)
