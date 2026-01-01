from django.urls import path , include
from . import views

urlpatterns = [
    path("",views.index_page,name="index_"),
    path("sign_up",views.signup_page,name="signup"),
    path("dashboard",views.dashboard_page,name="dashboard_"),
    path("dashboard/my_room",views.my_room_page,name="my_room_"),
    path("dashboard/select_room",views.select_room_page,name="select_room_"),
    path("dashboard/view_room/<int:pk>/",views.view_room,name="view_room_"),
    path("dashboard/book_room/<int:pk>/", views.book_room, name="book_room_action"),
    path("logout", views.logout_user, name="logout"), 
    path('dashboard/profile/', views.profile_view, name='profile_'),
    path('dashboard/profile/change_password', views.change_password, name='change_password_'),
]
