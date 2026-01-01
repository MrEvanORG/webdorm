from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Dorm, Block, Room, OtherInfo , Notice
from django.forms.models import BaseInlineFormSet

class WebDormAdminSite(admin.AdminSite):
    site_header = 'پنل مدیریت خوابگاه'
    site_title = 'پنل مدیریت'
    index_title = 'خوش آمدید'

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        for app in app_list:
            if app['app_label'] == 'myapp':
                app['name'] = 'مدیریت خوابگاه'
                custom_order = ['User', 'Dorm', 'Block', 'Room','Notice' 'OtherInfo']
                app['models'].sort(key=lambda x: custom_order.index(x['object_name']) if x['object_name'] in custom_order else len(custom_order))
        return app_list

super_admin_site = WebDormAdminSite(name='webdorm_admin')

class FloorFilter(admin.SimpleListFilter):
    title = 'طبقه'
    parameter_name = 'floor'

    def lookups(self, request, model_admin):
        floors = sorted(set(Room.objects.values_list('floor_number', flat=True)))
        return [(f, f"طبقه {f}") for f in floors]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(floor_number=self.value())
        return queryset


@admin.register(User, site=super_admin_site)
class CustomUserAdmin(UserAdmin):

    list_display = ('first_name', 'last_name', 'student_code', 'get_room_number', 'payed_cost', 'is_staff')

    list_filter = ('is_superuser', 'placed_in__placed_in', 'placed_in__placed_in__placed_in','payed_cost')

    search_fields = ('username', 'first_name', 'last_name', 'national_code', 'student_code')

    fieldsets = UserAdmin.fieldsets + (('اطلاعات دانشجویی', {'fields': ('national_code', 'student_code', 'placed_in', 'payed_cost')}),) # type: ignore
    add_fieldsets = UserAdmin.add_fieldsets + (('اطلاعات دانشجویی', {'fields': ('national_code', 'student_code', 'placed_in', 'payed_cost')}),)

    @admin.display(description='شماره اتاق')
    def get_room_number(self, obj):
        if obj.placed_in:
            return f"{obj.placed_in.number} ({obj.placed_in.placed_in.name})"
        return "-"


@admin.register(Dorm, site=super_admin_site)
class DormAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'total_capacity_display', 'current_population_display', 'is_active')

    list_editable = ('is_active',)

    @admin.display(description='ظرفیت کل')
    def total_capacity_display(self, obj): return obj.total_capacity

    @admin.display(description='ساکنین فعلی')
    def current_population_display(self, obj): return obj.current_population


@admin.register(Block, site=super_admin_site)
class BlockAdmin(admin.ModelAdmin):

    list_display = ('name', 'placed_in', 'floor_count', 'total_capacity_display', 'occupied_display', 'supervisor', 'is_active')

    list_filter = ('placed_in',)
    search_fields = ('name', 'supervisor__username')

    @admin.display(description='ظرفیت بلوک')
    def total_capacity_display(self, obj): return obj.total_capacity

    @admin.display(description='تعداد ساکنین')
    def occupied_display(self, obj): return obj.current_population


class StudentInlineFormSet(BaseInlineFormSet):
    def delete_existing(self, obj, commit=True):
        if commit:
            obj.placed_in = None
            obj.save()


class StudentInline(admin.TabularInline):
    model = User
    formset = StudentInlineFormSet 

    fields = ('first_name', 'last_name', 'student_code', 'national_code')
    readonly_fields = ('first_name', 'last_name', 'student_code', 'national_code')
    extra = 0 
    show_change_link = True
    verbose_name = "دانشجو"
    verbose_name_plural = "لیست دانشجویان (با تیک زدن حذف، دانشجو فقط از اتاق خارج می‌شود)"

@admin.register(Room, site=super_admin_site)
class RoomAdmin(admin.ModelAdmin):

    list_display = ('number', 'get_floor_display', 'get_dorm_name', 'placed_in', 'capacity', 'occupancy_display', 'is_active')
    
    list_filter = ('placed_in__placed_in', 'placed_in', FloorFilter, 'is_active')
    
    search_fields = ('number',)
    list_per_page = 20

    inlines = [StudentInline]

    @admin.display(description='طبقه', ordering='floor_number')
    def get_floor_display(self, obj):
        return f"طبقه {obj.floor_number}"

    @admin.display(description='خوابگاه', ordering='placed_in__placed_in')
    def get_dorm_name(self, obj): return obj.placed_in.placed_in.__str__()

    @admin.display(description='پر شده')
    def occupancy_display(self, obj): return obj.current_occupancy


@admin.register(OtherInfo, site=super_admin_site)
class OtherInfoAdmin(admin.ModelAdmin):
    list_display = ('start_selectroom_event', 'end_selectroom_event')
    def has_add_permission(self, request): return not OtherInfo.objects.exists()

@admin.register(Notice, site=super_admin_site)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'text')


