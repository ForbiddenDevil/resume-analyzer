# resume_analyzer/views.py
import os
from django.shortcuts import render
from dotenv import load_dotenv
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

load_dotenv()

def index(request):
    return render(request, 'index.html')

# Ensure you have your OpenAI API key set in your environment variables
# openai.api_key = os.getenv("OPENAI_API_KEY")

def chatbot_page(request):
    return render(request, 'chatbot.html')

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')
        # Send the user message to OpenAI and get the response using the new ChatCompletion API
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a hiring assistant"}, {"role": "user", "content": user_message}],
                stream=False
        )
        ai_message = response.choices[0].message.content.strip()
        
        return JsonResponse({'response': ai_message})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)