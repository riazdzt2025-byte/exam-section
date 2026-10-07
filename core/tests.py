from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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
