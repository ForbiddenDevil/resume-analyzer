from django.shortcuts import render

# Create your views here.
def resume_analytics(request):
    return render(request, 'resume_analytics/resume_analytics.html')