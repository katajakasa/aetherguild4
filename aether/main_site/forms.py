from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.db import transaction
from django.forms import CharField, EmailField, ModelForm, ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from aether.forum.models import ForumUser


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Change my password")))


class ConfirmResetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(ConfirmResetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Reset my password")))


class ResetPasswordForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Reset my password")))


class RegisterForm(UserCreationForm):
    email1 = EmailField(label=_("Email"))
    email2 = EmailField(
        label=_("Email confirmation"),
        help_text=_("Enter the same email as before, for verification."),
    )
    alias = CharField(label=_("User alias"), help_text=_("Username visible on the forums"), max_length=32)
    key = CharField(
        label=_("Registration key"),
        help_text=_("Registration token from any of the admins"),
        required=True,
        max_length=32,
    )

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Register")))

    def clean_email2(self):
        email1 = self.cleaned_data.get("email1")
        email2 = self.cleaned_data.get("email2")
        if email1 and email2 and email1 != email2:
            raise ValidationError(
                _("The two email fields didn't match."),
                code="email_mismatch",
            )
        if User.objects.filter(email=email2, is_active=True).exists():
            raise ValidationError(
                _("Given email is already in use"),
                code="email_in_use",
            )
        return email2

    def clean_key(self):
        key = self.cleaned_data.get("key")
        if key != settings.REGISTRATION_KEY:
            raise ValidationError(
                _("Invalid registration key"),
                code="key_mismatch",
            )

    @transaction.atomic
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email1"]
        if commit:
            user.save()

        profile = ForumUser(user=user, alias=self.cleaned_data["alias"])
        if commit:
            profile.save()

        return user, profile


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Login")))


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class ProfileForm(ModelForm):
    email = EmailField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get("instance").user
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields["email"].initial = self.user.email
        self.fields["signature"].widget.attrs["class"] = "bbcode_field"
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Save")))

    def save(self, *args, **kwargs):
        self.user.email = self.cleaned_data["email"]
        self.user.save()
        timezone.activate(str(self.cleaned_data["timezone"]))
        ret = super(ProfileForm, self).save(*args, **kwargs)
        return ret

    class Meta:
        model = ForumUser
        fields = ("alias", "email", "signature", "timezone", "message_limit", "thread_limit", "avatar")
