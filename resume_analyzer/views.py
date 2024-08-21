# resume_analyzer/views.py
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

@csrf_protect
def custom_login_view(request):
    if request.method == 'POST':
        host = request.POST.get('host')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, host=host, username=username, password=password)  # Uses custom backend
        
        if user is not None:
            login(request, user)  # Logs the user in
            messages.success(request, f'Welcome, {user.username}!')
            return redirect(request.POST.get('index', '/'))  # Redirect to a protected page
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'registration/login.html')
    else:
        return render(request, 'registration/login.html')

def custom_logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')