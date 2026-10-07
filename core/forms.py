from django import forms
from django.contrib.auth import get_user_model

from .models import Subject, Todo

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


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ["text"]
        widgets = {"text": forms.TextInput(attrs={"maxlength": 250})}

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if not text:
            raise forms.ValidationError("করণীয় লিখুন।")
        return text


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["owner", "name", "note"]
        widgets = {
            "name": forms.TextInput(attrs={"maxlength": 120}),
            "note": forms.TextInput(attrs={"maxlength": 200}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].queryset = User.objects.filter(is_active=True).order_by(
            "first_name", "username"
        )
        self.fields["owner"].label = "সদস্য"
        self.fields["owner"].label_from_instance = lambda user: (
            f"{user.first_name or user.username} ({user.username})"
        )
        self.fields["name"].label = "বিষয়"
        self.fields["note"].label = "নোট"
        self.fields["note"].required = False

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("বিষয়ের নাম লিখুন।")
        return name
