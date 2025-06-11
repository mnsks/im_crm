from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EntrepriseDonneuseOrdre, CentreAppels, ClientFinal
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'parent_centre', 'parent_entreprise', 'parent_client_entreprise')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'parent_centre', 'parent_entreprise', 'parent_client_entreprise')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(EntrepriseDonneuseOrdre)
admin.site.register(CentreAppels)
admin.site.register(ClientFinal)
