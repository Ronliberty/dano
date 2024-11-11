from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login
from .forms import UserProfileForm
from .models import UserProfile
from django.contrib.auth import get_user_model


User = get_user_model()
def role_based_redirect(request):
    if request.user.groups.filter(name='manager').exists():
        return redirect('dashboard:manager_dashboard')  # Define the URL name for manager dashboard
    else:
        return redirect('product:product-list')
def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product:product-list')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})



def accountSettings(request):
    # Ensure the user is in either 'default' or 'manager' group
    if not request.user.groups.filter(name__in=['Default', 'manager']).exists():
        return redirect('dashboard:client_dashboard')

    # Get or create a profile for the user
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileForm(instance=profile)

    # Redirect if a profile was just created and group is 'manager'
    if created:
        if request.user.groups.filter(name='manager').exists():
            return redirect('dashboard:manager_dashboard')
        elif request.user.groups.filter(name='Default').exists():
            return redirect('dashboard:client_dashboard')

    # Process the form if it's a POST request
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account:account')  # Reload page after saving to show success

    # Render the account settings form
    context = {'form': form}
    return render(request, 'account/account_settings.html', context)
