from django.shortcuts import render

# Create your views here.
def automated_screening(request):
    return render(request, 'automated_screening/automated_screening.html')