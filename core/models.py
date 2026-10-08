from django.conf import settings
from django.db import models


class Subject(models.Model):
    """একজন সদস্যের দায়িত্বে থাকা একটি বিষয় (জমা / টাইপ / ফটোকপি ট্র্যাকিংসহ)।"""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subjects"
    )
    name = models.CharField("বিষয়", max_length=120)
    note = models.CharField("নোট", max_length=200, blank=True)
    submitted = models.BooleanField("জমা পড়েছে", default=False)
    typed = models.BooleanField("টাইপ হয়েছে", default=False)
    photocopied = models.BooleanField("ফটোকপি হয়েছে", default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.owner} - {self.name}"

    @property
    def is_done(self):
        return self.submitted and self.typed and self.photocopied


class Todo(models.Model):
    """সদস্যের ব্যক্তিগত করণীয় তালিকা।"""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="todos"
    )
    text = models.CharField("করণীয়", max_length=250)
    done = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["done", "id"]

    def __str__(self):
        return self.text


class Activity(models.Model):
    """দৈনিক প্রতিবেদনের জন্য কাজের লগ — কে কবে কী করল।"""

    SUBJECT_ADD = "subject_add"
    SUBJECT_STATUS = "subject_status"
    SUBJECT_DELETE = "subject_delete"
    TODO_ADD = "todo_add"
    TODO_TOGGLE = "todo_toggle"
    TODO_DELETE = "todo_delete"

    KIND_CHOICES = [
        (SUBJECT_ADD, "বিষয় যোগ"),
        (SUBJECT_STATUS, "অবস্থা পরিবর্তন"),
        (SUBJECT_DELETE, "বিষয় মুছে ফেলা"),
        (TODO_ADD, "করণীয় যোগ"),
        (TODO_TOGGLE, "করণীয় হালনাগাদ"),
        (TODO_DELETE, "করণীয় মুছে ফেলা"),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities"
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    text = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created", "-id"]
        verbose_name_plural = "activities"

    def __str__(self):
        return f"{self.created:%Y-%m-%d %H:%M} {self.text}"


class AppSetting(models.Model):
    """সাধারণ সেটিংস (চাবি-মান), যেমন প্রতিবেদনের শিরোনাম।"""

    EXAM_TITLE = "exam_title"
    DEFAULT_EXAM_TITLE = "পরীক্ষা বিভাগ — কাজের অগ্রগতি"

    key = models.CharField(max_length=60, unique=True)
    value = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def get(cls, key, default=""):
        obj = cls.objects.filter(key=key).first()
        return obj.value if obj and obj.value else default

    @classmethod
    def set(cls, key, value):
        cls.objects.update_or_create(key=key, defaults={"value": value})

    @classmethod
    def exam_title(cls):
        return cls.get(cls.EXAM_TITLE, cls.DEFAULT_EXAM_TITLE)
