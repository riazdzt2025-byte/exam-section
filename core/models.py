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
