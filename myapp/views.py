from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, SignUpForm
from .models import User

def index(request):
    if request.user.is_authenticated:
        return redirect(dashboard_page)

    error_message = None
    student_id_value = ""

    if request.method == "POST":
        form = LoginForm(request.POST)
        student_id_value = request.POST.get('student_id', '') 

        if form.is_valid():
  
            student_code = form.cleaned_data.get('student_id')
            password = form.cleaned_data.get('password')

            try:
  
                user_obj = User.objects.get(student_code=student_code)
                
   
                user = authenticate(request, username=user_obj.username, password=password)

                if user is not None:
                    if user.is_active:
                        login(request, user)
  
                        request.session.set_expiry(15 * 24 * 60 * 60)
                        return redirect(dashboard_page)
                    else:
                        error_message = "حساب کاربری شما غیرفعال است."
                else:
                    error_message = "نام کاربری یا رمز عبور اشتباه است با پشتیبانی تماس بگیرید"
            except User.DoesNotExist:
                error_message = "نام کاربری یا رمز عبور اشتباه است با پشتیبانی تماس بگیرید"
        else:
            error_message = "فرمت وارد شده صحیح نیست."

    return render(request, "index.html", {
        "error_message": error_message,
        "student_id_value": student_id_value
    })


def signup_page(request):

    if request.user.is_authenticated:
        return redirect(dashboard_page)

    errors = {}
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data['student_id'], 
                student_code=form.cleaned_data['student_id'],
                national_code=form.cleaned_data['national_id'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password']
            )
            
            login(request, user)
            
            request.session.set_expiry(15 * 24 * 60 * 60)
            

            return redirect(dashboard_page)
        else:

            errors = form.errors

    return render(request, "sign_up.html", {
        "form_data": request.POST, 
        "errors": errors
    })


@login_required(login_url='index') 
def dashboard_page(request):
    return render(request, "dashboard.html")