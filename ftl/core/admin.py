from django.contrib import admin
# Register your models here.
from mptt.admin import MPTTModelAdmin

from core.models import FTLOrg, FTLUser, FTLDocument, FTLFolder

admin.site.register(FTLOrg)
admin.site.register(FTLUser)
admin.site.register(FTLDocument)
admin.site.register(FTLFolder, MPTTModelAdmin)
