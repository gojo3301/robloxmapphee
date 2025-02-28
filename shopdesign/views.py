from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required
def home(request):
    return render(request, "home.html", {})

@login_required
def user_logout(request):
    logout(request)
    return render(request, 'registration/user_logout.html')

def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect("shopdesign:login")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})