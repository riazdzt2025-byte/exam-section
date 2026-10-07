from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class MemberCreateForm(forms.Form):
    username = forms.CharField(label="ইউজারনেম", max_length=150)
    display_name = forms.CharField(label="নাম", max_length=150)
    password = forms.CharField(
        label="পাসওয়ার্ড",
        min_length=6,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    is_admin = forms.BooleanField(label="এডমিন", required=False)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("এই ইউজারনেম আগে থেকেই আছে।")
        return username

    def save(self):
        data = self.cleaned_data
        user = User(
            username=data["username"],
            first_name=data["display_name"].strip(),
            is_staff=data["is_admin"],
        )
        user.set_password(data["password"])
        user.save()
        return user


class SetMemberPasswordForm(forms.Form):
    password = forms.CharField(min_length=6)
