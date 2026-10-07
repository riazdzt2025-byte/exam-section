from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import MemberCreateForm, SetMemberPasswordForm

User = get_user_model()


def admin_required(view):
    """শুধু এডমিন (is_staff) ইউজার ঢুকতে পারবে।"""

    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper


@login_required
def home(request):
    done = Q(subjects__submitted=True, subjects__typed=True, subjects__photocopied=True)
    members = (
        User.objects.filter(is_active=True)
        .annotate(total=Count("subjects"), finished=Count("subjects", filter=done))
        .order_by("first_name", "username")
    )
    return render(request, "core/home.html", {"members": members})


@admin_required
def members(request):
    if request.method == "POST":
        form = MemberCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"সদস্য যোগ হয়েছে: {user.first_name}")
            return redirect("members")
    else:
        form = MemberCreateForm()
    users = User.objects.order_by("-is_active", "first_name", "username")
    return render(request, "core/members.html", {"form": form, "users": users})


@admin_required
@require_POST
def member_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = SetMemberPasswordForm(request.POST)
    if form.is_valid():
        user.set_password(form.cleaned_data["password"])
        user.save(update_fields=["password"])
        messages.success(request, f"{user.first_name or user.username}-এর নতুন পাসওয়ার্ড সেট হয়েছে।")
    else:
        messages.error(request, "পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।")
    return redirect("members")


@admin_required
@require_POST
def member_toggle(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "নিজের অ্যাকাউন্ট বন্ধ করা যাবে না।")
    else:
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        state = "চালু" if user.is_active else "বন্ধ"
        messages.success(request, f"{user.first_name or user.username}-এর অ্যাকাউন্ট {state} হয়েছে।")
    return redirect("members")


class MyPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = "core/password_change.html"
    success_url = reverse_lazy("home")
    success_message = "আপনার পাসওয়ার্ড বদলানো হয়েছে।"
