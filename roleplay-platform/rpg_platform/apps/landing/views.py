from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from rpg_platform.apps.accounts.forms import CustomUserCreationForm


def landing_page(request):
    """
    Landing page with registration and login forms
    """
    # Redirect authenticated users to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()

    return render(request, 'landing/home.html', {
        'login_form': login_form,
        'register_form': register_form,
    })


def terms_of_service(request):
    """
    Terms of Service page
    """
    return render(request, 'landing/terms_of_service.html')


def privacy_policy(request):
    """
    Privacy Policy page
    """
    return render(request, 'landing/privacy_policy.html')


def community_guidelines(request):
    """
    Community Guidelines page
    """
    return render(request, 'landing/community_guidelines.html')
