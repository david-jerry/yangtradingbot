from django.contrib import admin

from .models import CopyTradeAddresses, CustomUser
# Register your models here.
admin.site.register(CopyTradeAddresses)
admin.site.register(CustomUser)
