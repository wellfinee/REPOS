from django.contrib import admin
from . import models

# Если хочешь быстро посмотреть таблицы в админке — раскомментируй.
# admin.site.register(models.School)

admin.site.register(models.Parent)
admin.site.register(models.Teacher)
admin.site.register(models.Student)