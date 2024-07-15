from django import forms
from .models import JobApplication, Resume


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["job_description"]


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ["file"]


ResumeFormSet = forms.modelformset_factory(
    Resume, form=ResumeForm, extra=1, can_delete=True
)
