from django.contrib import admin

from .models import CopyTradeAddresses, CustomUser, Txhash
# Register your models here.
admin.site.register(CopyTradeAddresses)
admin.site.register(CustomUser)
admin.site.register(Txhash)
