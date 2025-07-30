from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, OutfitForm
from .models import Outfit

def index(request):
    form = OutfitForm()
    outfits = Outfit.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'index.html', {'form': form, 'outfits': outfits})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'index.html', {'form_type': 'signup', 'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
    return render(request, 'index.html', {'form_type': 'login'})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def upload_clothes(request):
    if request.method == 'POST':
        form = OutfitForm(request.POST, request.FILES)
        if form.is_valid():
            outfit = form.save(commit=False)
            outfit.user = request.user
            outfit.save()
    return redirect('index')

@login_required
def premium_payment(request):
    # This version just simulates a payment success message
    return render(request, 'index.html', {
        'form': OutfitForm(),
        'outfits': Outfit.objects.filter(user=request.user),
        'payment_success': True
    })