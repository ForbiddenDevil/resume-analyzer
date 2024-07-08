# named_entity_recognition/views.py
from django.shortcuts import render, redirect
from .forms import DocumentForm

def upload_resume(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = DocumentForm()
    return render(request, 'named_entity_recognition/upload_document.html', {'form': form})

def upload_success(request):
    return render(request, 'named_entity_recognition/success.html')
