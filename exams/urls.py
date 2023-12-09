from django.urls import path
from exams import views

urlpatterns = [
    path('exams/', views.read_exams, name='view exams'),
    path('exam/', views.create_or_update_exam, name="create/edit exam"),
    path('test/', views.read_or_create_test, name="do/view test"),
]