from django.contrib import admin
from django.contrib.auth.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_superuser')
    list_filter = ('is_superuser',)
    search_fields = ('username', 'email')
    readonly_fields = ('username', 'email', 'date_joined', 'last_login')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Only allow superusers to edit users
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False

from .models import Contact, Offer
admin.site.unregister(User)

class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "message")
    readonly_fields = [f.name for f in Contact._meta.fields]
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Name"
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Contact, ContactAdmin)
admin.site.register(User, UserAdmin)
