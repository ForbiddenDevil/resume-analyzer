from django.db import models


class JobApplication(models.Model):
    job_description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application {self.id}"


class Resume(models.Model):
    job_application = models.ForeignKey(
        JobApplication, related_name="resumes", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="candidate_matching/uploads")

    def __str__(self):
        return f"Resume for Application {self.job_application.id}"
