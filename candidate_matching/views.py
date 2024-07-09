from django.shortcuts import render

# Create your views here.
def candidate_matching(request):
    return render(request, 'candidate_matching/candidate_matching.html')