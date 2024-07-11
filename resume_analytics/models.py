from django.db import models

# Create your models here.
class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField(upload_to='resume_analytics/uploads')
    name = models.CharField(max_length=255, default='NA')