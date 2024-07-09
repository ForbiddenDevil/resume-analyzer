# named_entity_recognition/views.py
from django.shortcuts import render, redirect
from .forms import DocumentForm
from pypdf import PdfReader
from django.core.files.storage import FileSystemStorage
import os
import sys

sys.path.append(".")
from resume_analyzer import settings
import pathlib
import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")


def extract_ner_from_txt(sentence):
    doc = nlp(sentence)
    html = displacy.render(doc, style="ent", page=True)
    return html


def upload_resume(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        print("request.FILES1: ", request.FILES["upload"])
        if form.is_valid():
            # form.save()
            fs = FileSystemStorage()
            pdf_file = request.FILES["upload"]
            pdf_file_name = request.FILES["upload"].name
            filename = fs.save(
                os.path.join(settings.NER_MEDIA_ROOT, pdf_file.name), pdf_file
            )
            print(f"\n filename: {filename}")

            uploaded_file_path = os.path.join(settings.NER_MEDIA_ROOT, pdf_file_name)

            final_pdf_path = pathlib.Path(uploaded_file_path)
            print(f"final_pdf_path: {final_pdf_path}")
            reader = PdfReader(final_pdf_path)
            number_of_pages = len(reader.pages)
            print("---" * 25, "number_of_pages: ", number_of_pages)
            page = reader.pages[0]
            text = page.extract_text()

            # Do something with the extracted text
            print(text)
            response = extract_ner_from_txt(text)
            print("\n\n", "FINAL response: ", response)
            return render(
                request=request,
                template_name="named_entity_recognition/view_ner.html",
                context={"param1": response},
            )
            # return render(request, "file_display.html", {"file_data": file_data})
    else:
        form = DocumentForm()
    return render(
        request, "named_entity_recognition/upload_document.html", {"form": form}
    )


def upload_success(request):
    print("request.FILES", request.FILES)
    return render(request, "named_entity_recognition/success.html")


def named_entity_recognition(request):
    return render(request, "named_entity_recognition/named_entity_recognition.html")


def view_ner(request):
    return render(request, "named_entity_recognition/view_ner.html")
