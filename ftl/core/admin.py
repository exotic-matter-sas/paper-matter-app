from django.contrib import admin

# Register your models here.
from core.models import FTLOrg, FTLUser, FTLDocument

admin.site.register(FTLOrg)
admin.site.register(FTLUser)
admin.site.register(FTLDocument)
