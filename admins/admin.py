from django.contrib import admin
from users.models import openParkingSlot,CollegeParkingSlot,HospitalParkingSlot

# Register your models here.


class openParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('slot_id', 'vehicle_type', 'category', 'is_occupied')
    list_filter = ('vehicle_type', 'category', 'is_occupied')
    search_fields = ('slot_id', 'vehicle_type', 'category')

admin.site.register(openParkingSlot,openParkingSlotAdmin)

admin.site.register(CollegeParkingSlot)
admin.site.register(HospitalParkingSlot)