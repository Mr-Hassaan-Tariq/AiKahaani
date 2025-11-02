from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import CharField, ModelForm, PasswordInput

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


class UserChangeFormWithPassword(UserChangeForm):
    """
    Custom user change form with password confirmation fields.
    """

    password1 = CharField(
        label="New Password",
        widget=PasswordInput(attrs={"autocomplete": "new-password"}),
        required=False,
        help_text="Leave blank to keep the current password.",
    )
    password2 = CharField(
        label="Confirm New Password",
        widget=PasswordInput(attrs={"autocomplete": "new-password"}),
        required=False,
        help_text="Enter the same password as above, for verification.",
    )

    class Meta:
        model = User
        fields = "__all__"

    def clean_password2(self):
        """
        Validate that the two password entries match.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("The two password fields didn't match.")

        return password2

    def clean(self):
        """
        Validate password fields.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # If one password field is filled, both must be filled
        if password1 or password2:
            if not password1:
                raise ValidationError("Please fill in both password fields.")
            if not password2:
                raise ValidationError("Please confirm your password.")

        return cleaned_data

    def save(self, commit=True):
        """
        Save the user with hashed password.
        """
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")

        if password:
            user.set_password(password)  # This will hash the password

        if commit:
            user.save()
        return user


class UserCreationFormWithPassword(UserCreationForm):
    """
    Custom user creation form with proper password handling.
    """

    class Meta:
        model = User
        fields = ("email", "username", "fullname")

    def save(self, commit=True):
        """
        Save the user with hashed password.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # This will hash the password

        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeFormWithPassword
    add_form = UserCreationFormWithPassword

    list_display = (
        'id',
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
        (None, {"fields": ("email",)}),
        (
            "Password",
            {
                "fields": ("password1", "password2"),
                "description": "Enter a new password only if you want to change it. Leave blank to keep the current password.",
            },
        ),
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
