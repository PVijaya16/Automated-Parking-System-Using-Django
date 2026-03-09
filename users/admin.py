from django.contrib import admin
from .models import registrationmodel




class registredusers(admin.ModelAdmin):
  list_display = ("name", "email", "mobile","status")  
admin.site.register(registrationmodel, registredusers)






# class ParkingSessiontable(admin.ModelAdmin):
#   list_display = ("parking_slot", "vehicle_number", "entrance_time","exit_time","payment")  
# admin.site.register(ParkingSession, ParkingSessiontable)

