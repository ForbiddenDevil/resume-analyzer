from django.shortcuts import render, redirect
from .forms import DocumentForm
from pypdf import PdfReader
from django.core.files.storage import FileSystemStorage
import os
from resume_analyzer import settings
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def upload_document(request):
    if os.getenv("OPENAI_API_KEY") is None:
        return redirect("set_openai_api_key")
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage()
            pdf_file = request.FILES["upload"]
            pdf_file_name = request.FILES["upload"].name
            uploaded_file_path = os.path.join(settings.RA_MEDIA_ROOT, pdf_file_name)

            fs.save(uploaded_file_path, pdf_file)

            reader = PdfReader(uploaded_file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            summary_result = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Give a detailed summarization of given resume. Format the answer as unordered list in HTML inside a div tag. Do not return anything other than the list."}, {"role": "user", "content": text}],
                stream=False
            )

            weakness_result = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Give a detailed weaknesses of given resume. Format the answer as unordered list in HTML inside a div tag. Do not return anything other than the list."}, {"role": "user", "content": text}],
                stream=False
            )

            strength_result = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Give a detailed strengths of given resume. Format the answer as unordered list in HTML inside a div tag. Do not return anything other than the list."}, {"role": "user", "content": text}],
                stream=False
            )
            
            return render(
                request=request,
                template_name="resume_analytics/analyze.html",
                context={
                            "param1": summary_result.choices[0].message.content,
                            "param2": strength_result.choices[0].message.content,
                            "param3": weakness_result.choices[0].message.content,
                        },
            )
    else:
        form = DocumentForm()
    return render(request, 'resume_analytics/upload_document.html', {'form': form})

# Create your views here.
def resume_analytics(request):
    return render(request, 'resume_analytics/upload_document.html')