# resume_analytics/forms.py
from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    api_key = forms.CharField(widget=forms.PasswordInput, label='api_key')
    class Meta:
        model = Document
        fields = ('api_key', 'upload')