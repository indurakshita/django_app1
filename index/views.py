from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView
from django.db import IntegrityError
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import CustomSetPasswordForm, SignUpForm, ProfileForm, CustomPasswordResetForm, LoginForm
from .models import Profile
import time



# Create your views here.

def home(request):
    # if not request.user.is_authenticated:
    #     return redirect("login")
    return render(request, "index/home.html")

def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Successfully Logged in")
                print(f"Logged in {user}")
                return redirect("home")
            else:
                form.add_error('username', 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'index/login.html', {'form': form})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Successfully logged out!!")
    return redirect("home")

def signup(request):
    form = SignUpForm(request.POST or None)

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        try:
            if form.is_valid():
                user = form.save()
                user_profile, created = Profile.objects.get_or_create(user=user)
                if created:
                    messages.success(request, "Signup Successful")
                    login(request, user)
                    return redirect("home")
                else:
                    login(request, user)
                    return redirect("home")
        except IntegrityError:
            messages.error(request, "Error creating user profile. Please try again.")

    return render(request, "index/signup.html", context={"form": form})


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('password_reset')
    template_name = 'index/recovery/password_reset_form.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            password1 = form.cleaned_data.get('new_password1')
            password2 = form.cleaned_data.get('new_password2')
            if password1 == password2:
                user = form.save()
                login(request, user)
                messages.success(request, 'Password reset successfully.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Passwords do not match.')
        return self.form_invalid(form)


class CustomPasswordResetFormView(PasswordResetView):
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    template_name = 'index/recovery/password_reset_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Password reset email sent successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})


@login_required(login_url="/login")
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'index/profile.html', {'form': form})


