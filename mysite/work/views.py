from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

import fasttext
from PyPDF2 import PdfReader

import json
import os
import time

from work.forms import FileUploadForm
from work.models import FileProject


def index(request):
    return render(request, 'work/index.html')


def detect_short_language(text):
    german_short_words = ["das", "und", "tu", "zu", "von", "die", "was"]
    russian_short_words = ["и", "в", "не", "он", "на", "с", "что"]

    words = text.lower().split()

    german_count = sum(1 for word in words if word in german_short_words)
    russian_count = sum(1 for word in words if word in russian_short_words)

    total_words = len(words)

    if german_count > russian_count:
        language = "German"
        confidence = german_count / total_words
    elif russian_count > german_count:
        language = "Russian"
        confidence = russian_count / total_words
    else:
        language = "Unknown"
        confidence = 0.0

    return language, confidence


def detect_language(text):
    german_letters = set("abcdefghijklmnopqrstuvwxyzäöüß")
    russian_letters = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

    german_count = 0
    russian_count = 0

    for char in text.lower():
        if char in german_letters:
            german_count += 1
        elif char in russian_letters:
            russian_count += 1

    total_chars = len(text)
    german_confidence = german_count / total_chars
    russian_confidence = russian_count / total_chars

    if german_confidence > russian_confidence:
        return "German", german_confidence
    else:
        return "Russian", russian_confidence


def detect_view(request, file_id=None):
    file = FileProject.objects.get(id=file_id)
    start_time = time.time()
    file_extension = file.file.name.split(".")[-1].lower()
    if file_extension == 'pdf':
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        except FileNotFoundError:
            content = "File not found"

        language, confidence = detect_language(content)
        res_time = time.time() - start_time

        file_info = {
            'id': file.id,
            'name': str(file.file),
            'language': language,
            'confidence': confidence,
            'res_time': res_time
        }

    return render(request, 'work/process_pdf.html', {'file_info': file_info})


def dowland_detect_view(request, file_id=None):
    file = FileProject.objects.get(id=file_id)
    start_time = time.time()
    file_extension = file.file.name.split(".")[-1].lower()
    if file_extension == 'pdf':
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        except FileNotFoundError:
            content = "File not found"

        language, confidence = detect_language(content)
        res_time = time.time() - start_time

        file_info = {
            'id': file.id,
            'name': str(file.file),
            'language': language,
            'confidence': confidence,
        }
        file_info_json = json.dumps(file_info)

        response = HttpResponse(file_info_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="file_info.json"'
        return response

    return JsonResponse({'error': 'Invalid file extension'})


def dowland_detect_neuro_view(request, file_id=None):
    file = FileProject.objects.get(id=file_id)
    start_time = time.time()
    file_extension = file.file.name.split(".")[-1].lower()
    if file_extension == 'pdf':
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()

            # Remove newline characters from the content
            content = content.replace('\n', '')

            # Load the pre-trained language identification model
            model = fasttext.load_model('ai_model/lid.176.bin')

            # Detect the language of the content
            result = model.predict(content, k=3)

            # Extract the predicted labels and probabilities
            labels = result[0]
            probabilities = result[1]

            # Find the index of the label with the highest probability
            max_index = probabilities.argmax()

            # Get the language with the highest probability and its corresponding probability
            language = labels[max_index]
            probability = probabilities[max_index]

            file_info = {
                'id': file.id,
                'name': str(file.file),
                'language': language,
                'language_membership': {language: probability}
            }
            file_info_json = json.dumps(file_info)

            response = HttpResponse(file_info_json, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="file_info.json"'
            return response

        except:
            return JsonResponse({'error': 'Invalid file extension'})

    return JsonResponse({'error': 'Invalid file extension'})


def dowland_detect_short_view(request, file_id=None):
    file = FileProject.objects.get(id=file_id)
    start_time = time.time()
    file_extension = file.file.name.split(".")[-1].lower()
    if file_extension == 'pdf':
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        except FileNotFoundError:
            content = "File not found"

        language, confidence = detect_short_language(content)
        res_time = time.time() - start_time

        file_info = {
            'id': file.id,
            'name': str(file.file),
            'language': language,
            'confidence': confidence,
            'res_time': res_time
        }
        file_info_json = json.dumps(file_info)

        response = HttpResponse(file_info_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="file_info.json"'
        return response

    return JsonResponse({'error': 'Invalid file extension'})


def time_all_view(request):
    files = FileProject.objects.all()
    file_info_list = []

    max_neuro_time = 0
    max_frequency_time = 0
    max_short_time = 0

    for file in files:
        start_time = time.time()
        start_time1 = time.time()
        start_time2 = time.time()
        file_extension = file.file.name.split(".")[-1].lower()
        if file_extension == 'pdf':
            file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
            try:
                pdf_reader = PdfReader(file_path)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
            except FileNotFoundError:
                content = "File not found"

            content = content.replace('\n', '')

            model = fasttext.load_model('ai_model/lid.176.bin')

            result = model.predict(content, k=3)

            labels = result[0]
            probabilities = result[1]

            max_index = probabilities.argmax()

            language = labels[max_index]
            probability = probabilities[max_index]

            res_time_neuro = time.time() - start_time

            if res_time_neuro > max_neuro_time:
                max_neuro_time = res_time_neuro

            start_time = time.time()
            language1, confidence1 = detect_language(content)
            res_time_frequency = time.time() - start_time1

            if res_time_frequency > max_frequency_time:
                max_frequency_time = res_time_frequency

            start_time = time.time()
            language2, confidence2 = detect_short_language(content)
            res_time_short = time.time() - start_time2

            if res_time_short > max_short_time:
                max_short_time = res_time_short

            file_info = {
                'id': file.id,
                'name': str(file.file),
                'res_time_neuro': res_time_neuro,
                'res_time_frequency': res_time_frequency,
                'res_time_short': res_time_short
            }
            file_info_json = json.dumps(file_info)

            response = HttpResponse(file_info_json, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="file_info.json"'
            return response

        return JsonResponse({'error': 'Invalid file extension'})


def detect_all_view(request):
    files = FileProject.objects.all()
    file_info_list = []

    max_neuro_time = 0
    max_frequency_time = 0
    max_short_time = 0

    for file in files:
        start_time = time.time()
        start_time1 = time.time()
        start_time2 = time.time()
        file_extension = file.file.name.split(".")[-1].lower()
        if file_extension == 'pdf':
            file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
            try:
                pdf_reader = PdfReader(file_path)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
            except FileNotFoundError:
                content = "File not found"

            content = content.replace('\n', '')

            model = fasttext.load_model('ai_model/lid.176.bin')

            result = model.predict(content, k=3)

            labels = result[0]
            probabilities = result[1]

            max_index = probabilities.argmax()

            language = labels[max_index]
            probability = probabilities[max_index]

            res_time_neuro = time.time() - start_time

            if res_time_neuro > max_neuro_time:
                max_neuro_time = res_time_neuro

            start_time = time.time()
            language1, confidence1 = detect_language(content)
            res_time_frequency = time.time() - start_time1

            if res_time_frequency > max_frequency_time:
                max_frequency_time = res_time_frequency

            start_time = time.time()
            language2, confidence2 = detect_short_language(content)
            res_time_short = time.time() - start_time2

            if res_time_short > max_short_time:
                max_short_time = res_time_short

            file_info = {
                'id': file.id,
                'name': str(file.file),
                'res_time_neuro': res_time_neuro,
                'res_time_frequency': res_time_frequency,
                'res_time_short': res_time_short
            }
            file_info_list.append(file_info)

    return render(request, 'work/process_all_pdf.html',
                  {'file_info_list': file_info_list, 'max_neuro_time': max_neuro_time * 2.5,
                   'max_frequency_time': max_frequency_time, 'max_short_time': max_short_time})


def detect_short_view(request, file_id=None):
    file = FileProject.objects.get(id=file_id)
    start_time = time.time()
    file_extension = file.file.name.split(".")[-1].lower()
    if file_extension == 'pdf':
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        except FileNotFoundError:
            content = "File not found"

        language, confidence = detect_short_language(content)
        res_time = time.time() - start_time

        file_info = {
            'id': file.id,
            'name': str(file.file),
            'language': language,
            'confidence': confidence,
            'res_time': res_time
        }
    return render(request, 'work/process_short.html', {'file_info': file_info})


def detect_neuro_view(request, file_id=None):
    file = FileProject.objects.get(id=file_id)
    start_time = time.time()
    file_extension = file.file.name.split(".")[-1].lower()
    if file_extension == 'pdf':
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            pdf_reader = PdfReader(file_path)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()

            # Remove newline characters from the content
            content = content.replace('\n', '')

            # Load the pre-trained language identification model
            model = fasttext.load_model('ai_model/lid.176.bin')

            # Detect the language of the content
            result = model.predict(content, k=3)

            # Extract the predicted labels and probabilities
            labels = result[0]
            probabilities = result[1]

            # Find the index of the label with the highest probability
            max_index = probabilities.argmax()

            # Get the language with the highest probability and its corresponding probability
            language = labels[max_index]
            probability = probabilities[max_index]

            file_info = {
                'id': file.id,
                'name': str(file.file),
                'language': language,
                'language_membership': {language: probability}
            }
        except FileNotFoundError:
            content = "File not found"

    return render(request, 'work/process_neuro.html', {'file_info': file_info})


def project_view(request):
    project = FileProject.objects.all()
    file_info = []

    for file in project:
        file_extension = file.file.name.split(".")[-1].lower()
        if file_extension == 'pdf':
            file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
            try:
                pdf_reader = PdfReader(file_path)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
            except FileNotFoundError:
                content = "File not found"

            file_info.append(
                {
                    'id': file.id,
                    'name': str(file.file),
                    'content': content,
                })

    return render(request, 'work/project.html', {'file_info': file_info})


def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            return redirect('home')
    else:
        form = FileUploadForm()
    return render(request, 'work/index.html', {'form': form})


def delete_file(request, file_id):
    file_to_delete = FileProject.objects.get(pk=file_id)
    file_to_delete.file.delete()
    file_to_delete.delete()
    return redirect('home')


def view_file(request, file_id):
    file_object = get_object_or_404(FileProject, pk=file_id)
    response = HttpResponse(file_object.file.read(), content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename="{}"'.format(file_object.file.name)
    return response


def help_text(request):
    return render(request, 'work/help.html')
