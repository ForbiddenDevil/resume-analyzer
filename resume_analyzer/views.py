# resume_analyzer/views.py
import os
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse
from dotenv import load_dotenv

load_dotenv()

def index(request):
    return render(request, 'index.html')

@csrf_protect
def custom_login_view(request):
    if request.method == 'POST':
        host = request.POST.get('host')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, host=host, username=username, password=password)  # Uses custom backend
            if user is not None:
                login(request, user)  # Logs the user in
                return redirect(request.POST.get('index', '/'))  # Redirect to a protected page
            else:
                messages.error(request, 'Invalid username or password.')
                return render(request, 'registration/login.html')
        except:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'registration/login.html')
    else:
        return render(request, 'registration/login.html')

def custom_logout_view(request):
    logout(request)
    # Remove the OPENAI_API_KEY from the environment
    if os.getenv("OPENAI_API_KEY"):
        os.environ.pop("OPENAI_API_KEY")
    
    # Update the .env file to remove the OPENAI_API_KEY
    with open(".env", "r") as f:
        lines = f.readlines()
    
    with open(".env", "w") as f:
        for line in lines:
            if not line.startswith("OPENAI_API_KEY="):
                f.write(line)
    
    # Reload environment variables to reflect the changes
    load_dotenv()

    # Redirect to the login page or any other page
    return redirect("login")

def set_openai_api_key(request):
    if request.method == "POST":
        api_key = request.POST.get("api_key")

        if os.getenv("OPENAI_API_KEY"):
            os.environ.pop("OPENAI_API_KEY")
            
        if api_key:
            # Read the existing .env file content
            with open(".env", "r") as f:
                lines = f.readlines()

            # Update or add the OPENAI_API_KEY
            with open(".env", "w") as f:
                key_updated = False
                for line in lines:
                    if line.startswith("OPENAI_API_KEY="):
                        f.write(f"OPENAI_API_KEY={api_key}\n")
                        key_updated = True
                    else:
                        f.write(line)
                
                if not key_updated:
                    # If the key wasn't found and updated, add it
                    f.write(f"OPENAI_API_KEY={api_key}\n")

            # Reload environment variables to update them
            load_dotenv()
            return redirect("index")  # Redirect to the main page after setting the key

    return render(request, "set_api_key.html")
