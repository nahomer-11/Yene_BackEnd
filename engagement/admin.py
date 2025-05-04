from django.contrib import admin
from .models import Review, AdminNotification, UserHistory

# Register your models here.
admin.site.register(Review)
admin.site.register(AdminNotification)
admin.site.register(UserHistory)
