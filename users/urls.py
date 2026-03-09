from django.urls import path
from .import views
from .import hospital as hos
from .import loggins as lo
from .import parkinghistory as ph





urlpatterns = [
       path('registercheck/',views.registercheck,name='registercheck'),
       path('userlogin',views.userlogin,name='userlogin'),
       path('userlogincheck/',views.userlogincheck,name = 'userlogincheck'),
       path('userlogout/',views.userlogout,name='userlogout'),
       path('profile/', views.user_profile, name='userprofile'),
       path('update_profile/',views.update_profile,name='update_profile'),
       path('userhome/', views.user_home, name='userhome'),
       path('parkingentry/', views.parkingentry, name='parkingentry'),
       path('exitparking/', views.exitparking, name='exitparking'),
       path('parkinglogincheck/',lo.parkinglogincheck,name='parkinglogincheck'),
       path('openparkingfare/',views.openparkingfare,name='openparkingfare'),
       path('collegefare/',views.collegefare,name='collegefare'),
       path("submit-feedback/", views.submit_feedback, name="submit_feedback"),


       path('open-parking/', views.open_parking, name='open_parking'),
       path('confirm-parking/<int:slot_id>/', views.confirm_parking, name='confirm_parking'),
       path('checkout_parking/', views.checkout_parking, name='checkout_parking'),
       path('confirm-payment/<int:slot_id>/', views.confirm_payment, name='confirm_payment'),
       path('collegeparkingentry/', views.collegeparking, name='collegeparkingentry'),
       path('confirmcollegeparking/<str:slot_id>/', views.confirmcollegeparking, name='confirmcollegeparking'),
       path('collegecheckoutparking/', views.collegecheckoutparking, name='collegecheckoutparking'),
       path('collegeconfirmpayment/<str:slot_id>/', views.collegeconfirmpayment, name='collegeconfirmpayment'),
       # -----------hospital---------------------------------
       path('hospitalfare/', hos.hospitalfare, name='hospitalfare'),       
       path('hospitalparkigentry/', hos.hospitalparkigentry, name='hospitalparkigentry'),
       path('hospital_confirm_parking/<str:slot_id>/', hos.hospital_confirm_parking, name='hospital_confirm_parking'),
       path('hospital_checkout_parking/', hos.hospital_checkout_parking, name='hospital_checkout_parking'),
       path('hospitalconfirmpayment/<str:slot_id>/', hos.hospitalconfirmpayment, name='hospitalconfirmpayment'),
       # parking history

       path('parking_history/', ph.parking_history, name='parking_history'),
       path('college_parking_history/', ph.college_parking_history, name='college_parking_history'),
       path('hospital_parking_history/', ph.hospital_parking_history, name='hospital_parking_history'),

       




       



       





]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)