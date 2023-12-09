from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect

from users.forms import SignUpForm

# Create your views here.
def process_sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/users/login/")
    else:
        form = SignUpForm()
    return render(request, template_name='users/sign_up.html', context={'form': form})

def process_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        raw_password = request.POST['password']
        user = authenticate(request, username=email, password=raw_password)
        if user is not None:
            login(request, user)
            return redirect(to="/exams/exams/")
    return render(request, template_name='users/login.html')

def process_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect(to="/exams/exams/")
    return render(request, template_name='users/logout.html')
