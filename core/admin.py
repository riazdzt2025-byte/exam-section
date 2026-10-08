from django.contrib import admin

from .models import Activity, AppSetting, Subject, Todo


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "submitted", "typed", "photocopied")
    list_filter = ("owner",)


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ("text", "owner", "done")
    list_filter = ("owner", "done")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("created", "kind", "owner", "text")
    list_filter = ("kind", "owner")
    search_fields = ("text",)


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
