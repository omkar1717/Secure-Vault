from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import FileUpload
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from .encryption import encrypt_file
from .encryption import decrypt_file
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        return redirect('login')

    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    query = request.GET.get('q')

    if query:
        files = FileUpload.objects.filter(user=request.user, file__icontains=query)
    else:
        files = FileUpload.objects.filter(user=request.user)

    return render(request, 'dashboard.html', {'files': files})

@login_required
def upload_file(request):

    if request.method == "POST":

        uploaded_file = request.FILES['file']
        file_data = uploaded_file.read()

        encrypted_data = encrypt_file(file_data)

        with open(f"media/upload/{uploaded_file.name}", "wb") as f:
            f.write(encrypted_data)

        FileUpload.objects.create(
            user=request.user,
            file=f"upload/{uploaded_file.name}"
        )

        return redirect('dashboard')

    return render(request, 'upload.html')

@login_required
def download_file(request, file_id):

    file = FileUpload.objects.get(id=file_id, user=request.user)

    with open(file.file.path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_file(encrypted_data)

    response = HttpResponse(decrypted_data)
    response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'

    return response

@login_required
def delete_file(request, file_id):
    file = FileUpload.objects.get(id=file_id, user=request.user)
    file.delete()
    return redirect('dashboard')

