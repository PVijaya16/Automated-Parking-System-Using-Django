from django.urls import path
from . import views
from .import slots


urlpatterns = [
    path('AdminLogin/',views.AdminLogin, name='AdminLogin'),
    path("AdminLoginCheck/", views.AdminLoginCheck, name="AdminLoginCheck"),
    path("AdminHome/", views.AdminHome, name="AdminHome"),
    path('RegisterUsersView/', views.RegisterUsersView, name='RegisterUsersView'),
    path('activate_user/',views.activate_user,name = 'activate_user'),
    path('BlockUser/', views.BlockUser, name='BlockUser'),
    path('UnblockUser-user/', views.UnblockUser, name='UnblockUser'),
    path('adminlogout/',views.adminlogout,name='adminlogout'),
    path('parking-slots/', views.view_parking_slots, name='view_parking_slots'),
    path('view_college_parking_slots/', views.view_college_parking_slots, name='view_college_parking_slots'),
    path('hopitalparking/', views.hopitalparking, name='hopitalparking'),
    path('hospital_parking_first_floor_sloots/', views.hospital_parking_first_floor_sloots, name='hospital_parking_first_floor_sloots'),
    path('hospital_parking_second_floor_slots/', views.hospital_parking_second_floor_slots, name='hospital_parking_second_floor_slots'),
    path('hospital_parking_third_floor_slots/', views.hospital_parking_third_floor_slots, name='hospital_parking_third_floor_slots'),
    path('feedbackdata/', views.feedbackdata, name='feedbackdata'),

    # slots urls
    path('penparkingslots/', slots.penparkingslots, name='penparkingslots'),
    path('collegeparking/', slots.collegeparking, name='collegeparking'),
    path('hospitalparkingslots/', slots.hospitalparkingslots, name='hospitalparkingslots'),
  
]