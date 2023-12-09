from django.urls import path
from users import views

urlpatterns = [
    path('sign_up/', views.process_sign_up, name='sign up'),
    path('login/', views.process_login, name='login'),
    path('logout/', views.process_logout, name='logout')
]