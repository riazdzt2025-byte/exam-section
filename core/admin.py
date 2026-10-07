from django.contrib import admin

from .models import Subject, Todo


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "submitted", "typed", "photocopied")
    list_filter = ("owner",)


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ("text", "owner", "done")
    list_filter = ("owner", "done")
