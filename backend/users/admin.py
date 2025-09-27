from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Role, User


class UserAdminForm(ModelForm):
    """
    Custom form for User admin with validation.
    """

    class Meta:
        model = User
        fields = "__all__"

    def clean_email(self):
        """
        Validate email uniqueness.
        """
        email = self.cleaned_data.get("email")
        if email:
            # Check if email already exists (exclude current user if editing)
            queryset = User.objects.filter(email=email)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        """
        Validate username uniqueness.
        """
        username = self.cleaned_data.get("username")
        if username:
            # Check if username already exists (exclude current user if editing)
            queryset = User.objects.filter(username=username)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise ValidationError("A user with this username already exists.")
        return username

    def clean(self):
        """
        Validate password and roles requirements.
        """
        cleaned_data = super().clean()

        # Check if this is a new user (no pk) or password is being set
        if not self.instance.pk or self.data.get("password1"):
            password1 = self.data.get("password1")
            if not password1:
                raise ValidationError("Password is required for user creation.")

        return cleaned_data


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminForm

    list_display = (
        "email",
        "username",
        "fullname",
        "is_active",
        "is_staff",
        "get_roles_display",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "roles", "date_joined")
    search_fields = ("email", "username", "fullname")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("username", "fullname", "first_name", "last_name")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "roles",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "fullname", "password1", "password2"),
            },
        ),
        (
            "Permissions",
            {
                "classes": ("wide",),
                "fields": ("is_active", "is_staff", "is_superuser", "roles"),
            },
        ),
    )

    def get_roles_display(self, obj):
        """
        Display user roles as a comma-separated string.
        """
        roles = obj.roles.all()
        if roles:
            return ", ".join([role.name for role in roles])
        return "No roles"

    get_roles_display.short_description = "Roles"

    def clean_password2(self, form):
        """
        Validate that the two password entries match.
        """
        password1 = form.cleaned_data.get("password1")
        password2 = form.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def response_add(self, request, obj, post_url_continue=None):
        """
        Override to add validation warnings after user creation.
        """
        # Check if user has roles assigned
        if not obj.roles.exists():
            from django.contrib import messages

            messages.warning(
                request,
                "Warning: User was created without any roles assigned. Please edit the user to assign roles.",
            )

        return super().response_add(request, obj, post_url_continue)

    def get_form(self, request, obj=None, **kwargs):
        """
        Override to add custom validation messages.
        """
        form = super().get_form(request, obj, **kwargs)

        # Add help text for roles field
        if "roles" in form.base_fields:
            form.base_fields[
                "roles"
            ].help_text = 'Hold down "Control", or "Command" on a Mac, to select more than one. <strong>Warning:</strong> At least one role should be assigned.'
            form.base_fields["roles"].required = True

        return form


class RoleAdminForm(ModelForm):
    """
    Custom form for Role admin with validation.
    """

    class Meta:
        model = Role
        fields = "__all__"

    def clean_name(self):
        """
        Validate role name uniqueness.
        """
        name = self.cleaned_data.get("name")
        if name:
            # Check if role name already exists (exclude current role if editing)
            queryset = Role.objects.filter(name=name)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise ValidationError("A role with this name already exists.")
        return name


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin interface for Role model.
    """

    form = RoleAdminForm

    list_display = ("name", "created", "modified")
    list_filter = ("name", "created", "modified")
    search_fields = ("name",)
    ordering = ("name",)

    fieldsets = (
        (None, {"fields": ("name",)}),
        ("Timestamps", {"fields": ("created", "modified"), "classes": ("collapse",)}),
    )

    readonly_fields = ("created", "modified")
