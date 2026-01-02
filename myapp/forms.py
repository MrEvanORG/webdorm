from django import forms
from .models import User
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

def fix_numbers(text):
    if not text:
        return ""
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"
    table = str.maketrans(persian_digits + arabic_digits, english_digits + english_digits)
    return text.strip().translate(table)

class LoginForm(forms.Form):
    student_id = forms.CharField(
        label="کد دانشجویی",
        widget=forms.TextInput(attrs={'placeholder': 'مثال: 403123456'})
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={'placeholder': 'کلمه عبور خود را وارد کنید'})
    )

    def clean_student_id(self):
        return fix_numbers(self.cleaned_data.get('student_id'))


class SignUpForm(forms.Form):
    student_id = forms.CharField(
        max_length=9, 
        min_length=9,
        label="کد دانشجویی"
    )
    national_id = forms.CharField(
        max_length=10, 
        min_length=10,
        label="کد ملی"
    )
    first_name = forms.CharField(max_length=20, label="نام")
    last_name = forms.CharField(max_length=20, label="نام خانوادگی")
    password = forms.CharField(
        min_length=6, 
        label="رمز عبور",
        widget=forms.PasswordInput()
    )
    confirm_password = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput()
    )

    def clean_student_id(self):
        data = fix_numbers(self.cleaned_data.get('student_id'))
        
        if not data.isdigit() or len(data) != 9:
            raise forms.ValidationError("کد دانشجویی باید دقیقاً ۹ رقم عدد باشد.")
            
        if User.objects.filter(student_code=data).exists():
            raise forms.ValidationError("این شماره دانشجویی قبلاً در سامانه ثبت شده است.")
            
        return data

    def clean_national_id(self):
        data = fix_numbers(self.cleaned_data.get('national_id'))
        
        if not data.isdigit() or len(data) != 10:
            raise forms.ValidationError("کد ملی باید دقیقاً ۱۰ رقم عدد باشد.")
            
        if User.objects.filter(national_code=data).exists():
            raise forms.ValidationError("این کد ملی قبلاً در سامانه ثبت شده است.")
            
        return data

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:

            raise forms.ValidationError("رمز عبور با تکرار آن مطابقت ندارد.")
            
        return cleaned_data

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput,
        label="رمز عبور فعلی"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="رمز عبور جدید",
        min_length=8,
        error_messages={
            'min_length': 'رمز عبور باید حداقل ۸ کاراکتر باشد.'
        }
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="تکرار رمز عبور جدید"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user #add user field to form for validation
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("رمز عبور فعلی اشتباه است.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                self.add_error('confirm_password', "تکرار رمز عبور با رمز جدید مطابقت ندارد.")
        
        return cleaned_data

class UserProfileForm(forms.Form):
    first_name = forms.CharField(
        max_length=20,
        label="نام",
        required=True,
        error_messages={
            'max_length': 'نام نمی‌تواند بیشتر از ۲۰ کاراکتر باشد.',
            'required': 'وارد کردن نام الزامی است.'
        }
    )
    
    last_name = forms.CharField(
        max_length=20,
        label="نام خانوادگی",
        required=True,
        error_messages={
            'max_length': 'نام خانوادگی نمی‌تواند بیشتر از ۲۰ کاراکتر باشد.',
            'required': 'وارد کردن نام خانوادگی الزامی است.'
        }
    )
    

    email = forms.CharField(
        required=False,
        label="ایمیل",
        validators=[EmailValidator(message="لطفاً یک ایمیل معتبر وارد کنید.")]
    )

    def save_profile(self, user):
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        
        email_data = self.cleaned_data.get('email')
        # if email_data: #agar ino bezarim email karvar pak nemishe dige
        user.email = email_data
            
        user.save()