from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, SignUpForm
from .models import User, Notice, Room, Dorm, Block ,OtherInfo
from django.core.paginator import Paginator
from django.db.models import Count, F ,Max
from django.utils import timezone
from django.contrib import messages

def index_page(request):
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
  
                        request.session.set_expiry(15 * 24 * 60 * 60) #15 days
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
            
            request.session.set_expiry(15 * 24 * 60 * 60) #login after register 15 days
            

            return redirect(dashboard_page)
        else:

            errors = form.errors

    return render(request, "sign_up.html", {
        "form_data": request.POST, 
        "errors": errors
    })

@login_required(login_url='index_')
def select_room_page(request):
    user = request.user
    config = OtherInfo.get_instance()
    now = timezone.now()
    
    access_denied = False
    error_messages = []

    if not user.payed_cost:
        access_denied = True
        error_messages.append("هزینه اتاق توسط شما پرداخت نشده است.")

    if config.start_selectroom_event and now < config.start_selectroom_event:
        access_denied = True
        error_messages.append("زمان انتخاب اتاق هنوز فرا نرسیده است.")
    elif config.end_selectroom_event and now > config.end_selectroom_event:
        access_denied = True
        error_messages.append("مهلت انتخاب اتاق به پایان رسیده است.")

    if access_denied:
        return render(request, "select_room.html", {
            "access_denied": True,
            "error_messages": error_messages
        })
    #get parametrs from url
    dorm_id = request.GET.get('dorm')
    block_id = request.GET.get('block')
    floor = request.GET.get('floor')
    price_sort = request.GET.get('price_sort', '')
    capacity_sort = request.GET.get('capacity_sort', '')

    #find max floor
    max_floors_data = Block.objects.aggregate(max_f=Max('floor_count'))
    max_floors = max_floors_data.get('max_f') or 0
    floor_list = list(range(1, max_floors + 1)) #convert to list

    rooms_qs = Room.objects.filter(is_active=True).annotate(
        current_count=Count('students'),#num of students is not property of sql
        free_slots=F('capacity') - Count('students') #ظرفیت خالی
    )

    #اضافه شدن فیلتر به شرط های کوئری
    if dorm_id: rooms_qs = rooms_qs.filter(placed_in__placed_in_id=dorm_id)
    if block_id: rooms_qs = rooms_qs.filter(placed_in_id=block_id)
    if floor: rooms_qs = rooms_qs.filter(floor_number=floor)

    ordering = []
    #apply sortong by ....
    if capacity_sort == 'empty':
        ordering.append('-free_slots')
    elif capacity_sort == 'full':
        ordering.append('free_slots')

    if price_sort == 'cheap':
        ordering.append('room_cost')
    elif price_sort == 'expensive':
        ordering.append('-room_cost')

    ordering.append('number')
    rooms_qs = rooms_qs.order_by(*ordering)

    paginator = Paginator(rooms_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "select_room.html", {
        "rooms": page_obj,
        "dorms": Dorm.objects.filter(is_active=True),
        "blocks": Block.objects.filter(is_active=True),
        "floor_list": floor_list,
        "access_denied": False
    })

@login_required(login_url='index_')
def view_room(request,pk):
    user = request.user
    room = get_object_or_404(Room,pk=pk)
    roommates = []
    
    if room:
        roommates = room.students.all()
    
    return render(request, "view_room.html", {
        "room": room,
        "roommates": roommates
    })

@login_required(login_url='index_')
def book_room(request, pk):
    user = request.user
    room = get_object_or_404(Room, pk=pk)
    
    config = OtherInfo.get_instance()
    now = timezone.now()

    
    if not user.payed_cost:
        messages.error(request, "شما هنوز هزینه خوابگاه را پرداخت نکرده‌اید و مجاز به رزرو نیستید.")
        return redirect('select_room_')

    if config.start_selectroom_event and now < config.start_selectroom_event:
        messages.error(request, "زمان انتخاب اتاق هنوز فرا نرسیده است.")
        return redirect('select_room_')
    
    if config.end_selectroom_event and now > config.end_selectroom_event:
        messages.error(request, "مهلت انتخاب اتاق به پایان رسیده است.")
        return redirect('select_room_')


    if not room.is_active:
        messages.error(request, "این اتاق غیرفعال شده است.")
        return redirect('select_room_')

    if room.current_occupancy >= room.capacity:
        messages.error(request, "متاسفانه ظرفیت این اتاق همین الان تکمیل شد.")
        return redirect('select_room_')

    user.placed_in = room
    user.save()

    messages.success(request, f"اتاق {room.number} با موفقیت برای شما رزرو شد.")
    return redirect('dashboard_')

@login_required(login_url='index_') 
def my_room_page(request):
    user = request.user
    room = user.placed_in  #room
    roommates = []
    
    if room:
        #delete user
        roommates = room.students.exclude(id=user.id)
    
    return render(request, "my_room.html", {
        "room": room,
        "roommates": roommates
    })

@login_required(login_url='index_') 
def dashboard_page(request):
    notices = Notice.objects.all()
    context = {
        "notices":notices,
    }
    return render(request, "dashboard.html",context)

def logout_user(request):
    logout(request)
    return redirect('index_')


