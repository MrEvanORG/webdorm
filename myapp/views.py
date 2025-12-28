from django.shortcuts import render
# Create your views here.
def index(request):
    return render(request,"index.html")

def signup_page(request):
    return render(request,"sign_up.html")

def dashboard_page(request):
    return render(request,"dashboard.html")
