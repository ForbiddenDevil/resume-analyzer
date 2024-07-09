from django.shortcuts import render

# Create your views here.
def resume_generation(request):
    return render(request, 'resume_generation/resume_generation.html')