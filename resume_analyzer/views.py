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
