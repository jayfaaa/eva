from django.contrib import admin
from .models import EvaluationSheet, AppUser, Department, AppSettings


admin.site.register(EvaluationSheet)
admin.site.register(AppUser)
admin.site.register(Department)
admin.site.register(AppSettings)
