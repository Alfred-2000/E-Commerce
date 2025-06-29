from django.contrib import admin

from accounts import models as AccountsModels

admin.site.register(AccountsModels.MyUser)
admin.site.register(AccountsModels.Address)
admin.site.register(AccountsModels.UserSession)
