from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Subject, Todo

User = get_user_model()


class AuthFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin1", password="adminpass1", first_name="এডমিন", is_staff=True)

    def test_login_required_for_home(self):
        r = self.client.get(reverse("home"))
        self.assertRedirects(r, f"{reverse('login')}?next=/")

    def test_no_self_registration_url(self):
        self.assertEqual(self.client.get("/register/").status_code, 404)
        self.assertEqual(self.client.get("/signup/").status_code, 404)

    def test_admin_creates_member_and_member_can_login(self):
        self.client.login(username="admin1", password="adminpass1")
        r = self.client.post(reverse("members"), {
            "username": "saymun", "display_name": "সাইমুন হোসেন", "password": "secret12",
        })
        self.assertRedirects(r, reverse("members"))
        member = User.objects.get(username="saymun")
        self.assertFalse(member.is_staff)
        self.assertNotEqual(member.password, "secret12")  # হ্যাশ করা
        self.client.logout()
        self.assertTrue(self.client.login(username="saymun", password="secret12"))

    def test_admin_resets_member_password(self):
        member = User.objects.create_user("habib", password="oldpass12")
        self.client.login(username="admin1", password="adminpass1")
        self.client.post(reverse("member_password", args=[member.pk]), {"password": "newpass12"})
        self.client.logout()
        self.assertFalse(self.client.login(username="habib", password="oldpass12"))
        self.assertTrue(self.client.login(username="habib", password="newpass12"))

    def test_short_password_rejected(self):
        member = User.objects.create_user("emon", password="oldpass12")
        self.client.login(username="admin1", password="adminpass1")
        self.client.post(reverse("member_password", args=[member.pk]), {"password": "123"})
        member.refresh_from_db()
        self.assertTrue(member.check_password("oldpass12"))

    def test_member_cannot_manage_members(self):
        User.objects.create_user("sorab", password="memberpass1")
        self.client.login(username="sorab", password="memberpass1")
        self.assertEqual(self.client.get(reverse("members")).status_code, 403)
        victim = User.objects.create_user("x", password="oldpass12")
        r = self.client.post(reverse("member_password", args=[victim.pk]), {"password": "hacked123"})
        self.assertEqual(r.status_code, 403)
        victim.refresh_from_db()
        self.assertTrue(victim.check_password("oldpass12"))

    def test_admin_cannot_deactivate_self(self):
        self.client.login(username="admin1", password="adminpass1")
        self.client.post(reverse("member_toggle", args=[self.admin.pk]))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_deactivated_member_cannot_login(self):
        m = User.objects.create_user("off", password="memberpass1", is_active=False)
        self.assertFalse(self.client.login(username="off", password="memberpass1"))


class TasksPageTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "taskadmin", password="adminpass1", first_name="এডমিন", is_staff=True
        )
        self.member = User.objects.create_user(
            "taskmember", password="memberpass1", first_name="সদস্য"
        )
        self.other = User.objects.create_user(
            "othermember", password="otherpass1", first_name="অন্য সদস্য"
        )

    def test_tasks_page_requires_login(self):
        response = self.client.get(reverse("tasks"))
        self.assertRedirects(response, f"{reverse('login')}?next=/tasks/")

    def test_member_can_add_and_view_private_todo(self):
        self.client.login(username="taskmember", password="memberpass1")
        response = self.client.post(
            reverse("tasks"), {"action": "add_todo", "text": "  কাগজ যাচাই  "}
        )
        self.assertRedirects(response, reverse("tasks"))
        todo = Todo.objects.get()
        self.assertEqual(todo.owner, self.member)
        self.assertEqual(todo.text, "কাগজ যাচাই")
        self.assertFalse(todo.done)
        self.assertContains(self.client.get(reverse("tasks")), "কাগজ যাচাই")

    def test_member_can_toggle_and_delete_own_todo(self):
        todo = Todo.objects.create(owner=self.member, text="নথি গোছানো")
        self.client.login(username="taskmember", password="memberpass1")
        response = self.client.post(
            reverse("todo_toggle", args=[todo.pk]), {"value": "1"}
        )
        self.assertRedirects(response, reverse("tasks"))
        todo.refresh_from_db()
        self.assertTrue(todo.done)
        response = self.client.post(reverse("todo_delete", args=[todo.pk]))
        self.assertRedirects(response, reverse("tasks"))
        self.assertFalse(Todo.objects.filter(pk=todo.pk).exists())

    def test_member_cannot_change_another_members_todo(self):
        todo = Todo.objects.create(owner=self.other, text="গোপন করণীয়")
        self.client.login(username="taskmember", password="memberpass1")
        self.assertEqual(
            self.client.post(reverse("todo_toggle", args=[todo.pk]), {"value": "1"}).status_code,
            404,
        )
        self.assertEqual(self.client.post(reverse("todo_delete", args=[todo.pk])).status_code, 404)
        todo.refresh_from_db()
        self.assertFalse(todo.done)

    def test_members_only_see_and_update_their_assigned_subjects(self):
        own_subject = Subject.objects.create(owner=self.member, name="বাংলা")
        other_subject = Subject.objects.create(owner=self.other, name="ইংরেজি")
        self.client.login(username="taskmember", password="memberpass1")
        response = self.client.get(reverse("tasks"))
        self.assertContains(response, "বাংলা")
        self.assertNotContains(response, "ইংরেজি")

        response = self.client.post(
            reverse("subject_step", args=[own_subject.pk, "submitted"]), {"value": "1"}
        )
        self.assertRedirects(response, reverse("tasks"))
        own_subject.refresh_from_db()
        self.assertTrue(own_subject.submitted)

        response = self.client.post(
            reverse("subject_step", args=[other_subject.pk, "submitted"]), {"value": "1"}
        )
        self.assertEqual(response.status_code, 404)
        other_subject.refresh_from_db()
        self.assertFalse(other_subject.submitted)

    def test_staff_can_assign_subject_to_active_member(self):
        self.client.login(username="taskadmin", password="adminpass1")
        response = self.client.post(
            reverse("tasks"),
            {
                "action": "add_subject",
                "owner": self.member.pk,
                "name": "গণিত",
                "note": "প্রশ্নপত্র প্রস্তুত",
            },
        )
        self.assertRedirects(response, reverse("tasks"))
        subject = Subject.objects.get()
        self.assertEqual(subject.owner, self.member)
        self.assertEqual(subject.note, "প্রশ্নপত্র প্রস্তুত")
        self.assertContains(self.client.get(reverse("tasks")), "গণিত")

    def test_member_cannot_assign_or_delete_subjects(self):
        subject = Subject.objects.create(owner=self.member, name="বিজ্ঞান")
        self.client.login(username="taskmember", password="memberpass1")
        response = self.client.post(
            reverse("tasks"),
            {"action": "add_subject", "owner": self.member.pk, "name": "নতুন"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(
            self.client.post(reverse("subject_delete", args=[subject.pk])).status_code, 403
        )
        self.assertTrue(Subject.objects.filter(pk=subject.pk).exists())

    def test_invalid_task_actions_and_status_values_are_rejected(self):
        subject = Subject.objects.create(owner=self.member, name="ইতিহাস")
        todo = Todo.objects.create(owner=self.member, text="সিলেবাস দেখা")
        self.client.login(username="taskmember", password="memberpass1")
        self.assertEqual(self.client.post(reverse("tasks"), {"action": "other"}).status_code, 400)
        self.assertEqual(
            self.client.post(
                reverse("subject_step", args=[subject.pk, "owner"]), {"value": "1"}
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse("todo_toggle", args=[todo.pk]), {"value": "not-a-bool"}
            ).status_code,
            400,
        )
