from django.shortcuts import render

# Create your views here.
def resume_classification(request):
    return render(request, 'resume_classification/resume_classification.html')