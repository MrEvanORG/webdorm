from django.urls import path , include
from . import views

urlpatterns = [
    path("",views.index,name="index"),
    path("sign_up",views.signup_page,name="signup"),
    path("dashboard",views.dashboard_page,name="dashboard_"),
]
