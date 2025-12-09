from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    first_name = models.CharField(max_length=20, verbose_name='نام')
    last_name = models.CharField(max_length=20, verbose_name='نام خانوادگی')
    national_code = models.CharField(max_length=10, verbose_name='کد ملی')
    student_code = models.CharField(max_length=9, verbose_name='شماره دانشجویی')
    placed_in = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='محل دانشجو', related_name='students')
    payed_cost = models.BooleanField(verbose_name='وضعیت پرداخت هزینه اتاق', default=False)

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


class OtherInfo(models.Model):
    start_selectroom_event = models.DateTimeField(verbose_name='آغاز زمان انتخاب اتاق')
    end_selectroom_event = models.DateTimeField(verbose_name='پایان زمان انتخاب اتاق')

    def __str__(self):
        return "تنظیمات زمان بندی"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "تنظیمات زمان‌بندی"
        verbose_name_plural = "تنظیمات زمان‌بندی"


class Dorm(models.Model):
    class GenderChoices(models.TextChoices):
        male = "male", "آقایان"
        female = "female", "خانم ها"
        married = "married", "متاهلی"

    name = models.CharField(max_length=64, verbose_name='نام خوابگاه')
    gender = models.CharField(max_length=8, choices=GenderChoices, verbose_name='جنسیت دانشجویان')
    is_active = models.BooleanField(verbose_name='وضعیت فعال بودن', default=True)

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"

    @property
    def total_capacity(self):
        return sum(block.total_capacity for block in self.block_set.all())

    @property
    def current_population(self):
        return sum(block.current_population for block in self.block_set.all())

    class Meta:
        verbose_name = "خوابگاه"
        verbose_name_plural = "خوابگاه ها"
        ordering = ['-id']


class Block(models.Model):
    name = models.CharField(max_length=64, verbose_name='نام بلوک')
    placed_in = models.ForeignKey(Dorm, on_delete=models.PROTECT, verbose_name='واقع در')
    floor_count = models.PositiveIntegerField(verbose_name='تعداد طبقه')
    floor_rooms = models.PositiveIntegerField(verbose_name='تعداد اتاق در هر طبقه')
    default_room_capacity = models.PositiveIntegerField(verbose_name='ظرفیت پیش‌ فرض هر اتاق', default=6)
    room_costs = models.PositiveIntegerField(verbose_name='هزینه اتاق ها')
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='مدیر بلوک', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='وضعیت فعال بودن', default=True)

    def __str__(self):
        return f"{self.name} - {self.placed_in.name}"

    @property
    def total_capacity(self):
        return sum(room.capacity for room in self.room_set.all())

    @property
    def current_population(self):
        return sum(room.current_occupancy for room in self.room_set.all())

    def save(self, *args, **kwargs):
        if self.placed_in.gender == 'married':
            self.default_room_capacity = 2
            
        is_new = self.pk is None
        super().save(*args, **kwargs)
        

        if is_new:
            self.create_rooms_automatically()

    def create_rooms_automatically(self):
        rooms_list = []
        for i in range(self.floor_count):
            current_floor = i + 1
            floor_prefix = current_floor * 100
            
            for r in range(1, self.floor_rooms + 1):
                rooms_list.append(Room(
                    number=floor_prefix + r,
                    floor_number=current_floor,
                    room_cost=self.room_costs,
                    placed_in=self,
                    capacity=self.default_room_capacity,
                    is_active=True
                ))
        Room.objects.bulk_create(rooms_list)

    class Meta:
        verbose_name = "بلوک"
        verbose_name_plural = "بلوک ها"
        ordering = ['-id']


class Room(models.Model):
    number = models.PositiveIntegerField(verbose_name='شماره اتاق')
    floor_number = models.IntegerField(verbose_name='طبقه اتاق')
    room_cost = models.IntegerField(verbose_name='هزینه اتاق', default=0)
    placed_in = models.ForeignKey(Block, on_delete=models.PROTECT, verbose_name='در بلوک')
    capacity = models.IntegerField(verbose_name='ظرفیت اتاق', default=6)
    is_active = models.BooleanField(verbose_name='وضعیت فعال بودن', default=True)

    def __str__(self):
        return f"اتاق {self.number} ({self.placed_in.name})"

    @property
    def current_occupancy(self):
        return self.students.count()

    @property
    def free_capacity(self):
        return self.capacity - self.current_occupancy

    class Meta:
        verbose_name = "اتاق"
        verbose_name_plural = "اتاق ها"
        ordering = ['number']