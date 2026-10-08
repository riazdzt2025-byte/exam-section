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


class SubjectForm(forms.Form):
    name = forms.CharField(label="বিষয়ের নাম", max_length=120)
    note = forms.CharField(label="নোট", max_length=200, required=False)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("বিষয়ের নাম লিখুন।")
        return name


class TodoForm(forms.Form):
    text = forms.CharField(label="করণীয়", max_length=250)

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if not text:
            raise forms.ValidationError("করণীয় লিখুন।")
        return text


class ExcelImportForm(forms.Form):
    file = forms.FileField(label="এক্সেল ফাইল (.xlsx)")

    def clean_file(self):
        f = self.cleaned_data["file"]
        if not f.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("শুধু .xlsx ফাইল গ্রহণ করা হয়।")
        return f


class SettingsForm(forms.Form):
    exam_title = forms.CharField(label="প্রতিবেদনের শিরোনাম", max_length=200)

    def clean_exam_title(self):
        value = self.cleaned_data["exam_title"].strip()
        if not value:
            raise forms.ValidationError("শিরোনাম খালি রাখা যাবে না।")
        return value
