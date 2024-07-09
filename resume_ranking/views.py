from django.shortcuts import render

# Create your views here.
def resume_ranking(request):
    return render(request, 'resume_ranking/resume_ranking.html')