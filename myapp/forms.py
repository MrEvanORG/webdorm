from django import forms
from .models import User

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