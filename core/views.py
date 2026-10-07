from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods, require_POST

from .forms import MemberCreateForm, SetMemberPasswordForm, SubjectForm, TodoForm
from .models import Subject, Todo

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


@login_required
@require_http_methods(["GET", "POST"])
def tasks(request):
    todo_form = TodoForm()
    subject_form = SubjectForm() if request.user.is_staff else None

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_todo":
            todo_form = TodoForm(request.POST)
            if todo_form.is_valid():
                todo = todo_form.save(commit=False)
                todo.owner = request.user
                todo.save()
                messages.success(request, "করণীয় যোগ হয়েছে।")
                return redirect("tasks")
        elif action == "add_subject":
            if not request.user.is_staff:
                raise PermissionDenied
            subject_form = SubjectForm(request.POST)
            if subject_form.is_valid():
                subject_form.save()
                messages.success(request, "বিষয় বরাদ্দ হয়েছে।")
                return redirect("tasks")
        else:
            return HttpResponseBadRequest("Unknown task action.")

    if request.user.is_staff:
        subjects = Subject.objects.select_related("owner").order_by(
            "owner__first_name", "owner__username", "order", "id"
        )
    else:
        subjects = request.user.subjects.all()

    return render(
        request,
        "core/tasks.html",
        {
            "todo_form": todo_form,
            "todos": request.user.todos.all(),
            "subject_form": subject_form,
            "subjects": subjects,
        },
    )


@login_required
@require_POST
def subject_step(request, pk, field):
    if field not in {"submitted", "typed", "photocopied"}:
        raise Http404
    value = request.POST.get("value")
    if value not in {"0", "1"}:
        return HttpResponseBadRequest("Invalid status value.")

    subject_scope = Subject.objects.all()
    if not request.user.is_staff:
        subject_scope = subject_scope.filter(owner=request.user)
    subject = get_object_or_404(subject_scope, pk=pk)
    new_value = value == "1"
    if getattr(subject, field) != new_value:
        setattr(subject, field, new_value)
        subject.save(update_fields=[field])
    return redirect("tasks")


@login_required
@require_POST
def todo_toggle(request, pk):
    value = request.POST.get("value")
    if value not in {"0", "1"}:
        return HttpResponseBadRequest("Invalid status value.")
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    todo.done = value == "1"
    todo.save(update_fields=["done"])
    return redirect("tasks")


@login_required
@require_POST
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    todo.delete()
    messages.success(request, "করণীয় মুছে ফেলা হয়েছে।")
    return redirect("tasks")


@admin_required
@require_POST
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    subject.delete()
    messages.success(request, "বিষয়টি সরানো হয়েছে।")
    return redirect("tasks")


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
