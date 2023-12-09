from django.contrib import admin
from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from users.models import User
from exams.models import Exam, Test
import datetime
import random

# Register your models here.
class ExamAdmin(admin.ModelAdmin):
    # The fields to be used in displaying the Exam model.
    # that reference specific fields on exmas.Exam.
    list_display = ["name", "code", "begin_on", "end_on"]
    list_filter = ["created_by"]
    readonly_fields = ("created_on", "created_by")
    search_fields = ["id"]
    ordering = ["id"]
    filter_horizontal = []

# Now register the new ExamAdmin...
admin.site.register(Exam, ExamAdmin)
# # ... and, since we're not using Django's built-in permissions,
# # unregister the Group model from admin.
# admin.site.unregister(Group)

class TestAdmin(admin.ModelAdmin):
    # The fields to be used in displaying the Exam model.
    # that reference specific fields on exmas.Exam.
    list_display = ["name", "code", "exam_id", "score"]
    list_filter = ["created_by"]
    readonly_fields = ("created_on", "created_by", "exam_id", "score")
    search_fields = ["id"]
    ordering = ["id"]
    filter_horizontal = []

# Now register the new ExamAdmin...
admin.site.register(Test, TestAdmin)
# # ... and, since we're not using Django's built-in permissions,
# # unregister the Group model from admin.
# admin.site.unregister(Group)