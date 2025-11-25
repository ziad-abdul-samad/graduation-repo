from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Student)
admin.site.register(models.Supervisor)
admin.site.register(models.Major)
admin.site.register(models.University)
admin.site.register(models.Projects)
admin.site.register(models.Ratings)
admin.site.register(models.ProjectPictures)
admin.site.register(models.ProjectMedia)
admin.site.register(models.AdminUser)
admin.site.register(models.Skills)
admin.site.register(models.StudentDetails)
admin.site.register(models.Comments)