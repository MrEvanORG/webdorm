from django.urls import path , include
from . import views

urlpatterns = [
    path("",views.index_page,name="index_"),
    path("sign_up",views.signup_page,name="signup"),
    path("dashboard",views.dashboard_page,name="dashboard_"),
    path("my_room",views.my_room_page,name="my_room_"),
    path("select_room",views.select_room_page,name="select_room_"),
]
