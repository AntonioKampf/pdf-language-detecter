from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('project_print/', project_view, name='project_view'),
    path('help/',help_text,name='help_text'),
    path('upload/', upload_file, name='upload_file'),
    path('delete/<int:file_id>/', delete_file, name='delete_file'),
    path('view_file/<int:file_id>/', view_file, name='view_file'),
    path('detect_view/<int:file_id>/', detect_view, name='detect_view'),
    path('dowland_detect_view/<int:file_id>/', dowland_detect_view, name='dowland_detect_view'),
    path('detect_short_view/<int:file_id>/', detect_short_view, name='detect_short_view'),
    path('dowland_detect_short_view/<int:file_id>/', dowland_detect_short_view, name='dowland_detect_short_view'),
    path('detect_neuro_view/<int:file_id>/', detect_neuro_view, name='detect_neuro_view'),
    path('dowland_detect_neuro_view/<int:file_id>/', dowland_detect_neuro_view, name='dowland_detect_neuro_view'),
    path('detect_all_view/', detect_all_view, name='detect_all_view'),
    path('view_file/<int:file_id>', view_file, name='view_file'),
    path('time_all_view/', time_all_view, name='time_all_view'),
]
