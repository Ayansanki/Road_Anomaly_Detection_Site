from django.contrib import admin
from road_anomaly_detection_app import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.RoadAnomalyReport)
admin.site.register(models.MediaContent)