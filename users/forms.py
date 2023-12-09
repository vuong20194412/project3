from django import forms
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import datetime

from users.models import User, generate_code

class SignUpForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    password = forms.CharField(
        label=_("Mật khẩu"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    repeated_password = forms.CharField(
        label=_("Xác nhận mật khẩu"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Nhập lại mật khẩu, để xác nhận."),
    )

    class Meta:
        model = User
        fields = ["email", "name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = True

    def clean_repeated_password(self):
        password = self.cleaned_data.get("password")
        repeated_password = self.cleaned_data.get("repeated_password")
        if password and repeated_password and password != repeated_password:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return repeated_password

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        repeated_password = self.cleaned_data.get("repeated_password")
        if repeated_password:
            try:
                password_validation.validate_password(repeated_password, self.instance)
            except ValidationError as error:
                self.add_error("repeated_password", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.code = generate_code()
        user.created_on = datetime.datetime.now(datetime.timezone.utc)
        user.updated_on = datetime.datetime.now(datetime.timezone.utc)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
