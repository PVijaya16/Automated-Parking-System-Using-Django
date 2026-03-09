from django.db import models
from django.utils.timezone import now


class registrationmodel(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)
    mobile = models.CharField(unique=True,max_length=20)
    status = models.CharField(max_length=100, default='waiting')
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=now) 
    
    
    def __str__(self):
        return self.name




from django.db import models
from django.utils.timezone import now


class openParkingSlot(models.Model):
    TYPE_CHOICES = [
        ('2W', '2-Wheeler'),
        ('4W', '4-Wheeler'),
    ]

    CATEGORY_CHOICES = [
        ('Regular', 'Regular'),
        ('VIP', 'VIP'),
    ]

    slot_id = models.AutoField(primary_key=True)
    vehicle_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Regular')
    is_occupied = models.BooleanField(default=False)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)  # Track vehicle number
    entry_time = models.DateTimeField(blank=True, null=True)  # Track entry time
    exit_time = models.DateTimeField(blank=True, null=True)  # Track exit time
    payment_status = models.BooleanField(default=False)  # Track payment status

    def __str__(self):
        status = "Occupied" if self.is_occupied else "Available"
        return f"Slot {self.slot_id}: {self.vehicle_type} | {self.category} | {status}"

class CollegeParkingSlot(models.Model):
    TYPE_CHOICES = [
        ('2W', '2-Wheeler'),
        ('4W', '4-Wheeler'),
    ]

    CATEGORY_CHOICES = [
        ('Student', 'Student'),
        ('Visitor', 'Visitor'),
        ('Faculty', 'Faculty'),
    ]

    slot_id = models.CharField(max_length=10, unique=True, blank=True) 
    vehicle_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    is_occupied = models.BooleanField(default=False)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)  # Track vehicle number
    entry_time = models.DateTimeField(blank=True, null=True)  # Track entry time
    exit_time = models.DateTimeField(blank=True, null=True)  # Track exit time
    payment_status = models.BooleanField(default=False)  # Track payment status
    payment_details = models.TextField(blank=True, null=True)  # Store additional payment information if needed


    def save(self, *args, **kwargs):
        if not self.slot_id:
            self.slot_id = f"{self.category[:2].upper()}{str(self.pk).zfill(4)}"  # Example: ST0001
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Occupied" if self.is_occupied else "Available"
        return f"Slot {self.slot_id}: {self.vehicle_type} | {self.category} | {status}"

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

class HospitalParkingSlot(models.Model):
    TYPE_CHOICES = [
        ('2W', '2-Wheeler'),
        ('4W', '4-Wheeler'),
    ]

    CATEGORY_CHOICES = [
        ('Patient', 'Patient'),
        ('Staff', 'Staff'),
        ('VIP', 'VIP'),
    ]

    slot_id = models.CharField(max_length=10, unique=True, blank=True)  # Unique slot identifier
    vehicle_type = models.CharField(max_length=2, choices=TYPE_CHOICES)  # Type of vehicle (2W or 4W)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)  # Parking category
    is_occupied = models.BooleanField(default=False)  # Slot availability status
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)  # Vehicle number
    entry_time = models.DateTimeField(blank=True, null=True)  # Entry time
    exit_time = models.DateTimeField(blank=True, null=True)  # Exit time
    payment_status = models.BooleanField(default=False)  # Payment status
    payment_details = models.TextField(blank=True, null=True)  # Payment info
    floor = models.CharField(max_length=20) # Floor number

    def save(self, *args, **kwargs):
        if not self.slot_id:
            self.slot_id = f"{self.category[:2].upper()}{self.floor}-{str(self.pk).zfill(4)}"  # Example: PA1-0001
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Occupied" if self.is_occupied else "Available"
        return f"Floor {self.floor} | Slot {self.slot_id}: {self.vehicle_type} | {self.category} | {status} | "


from django.db import models
from django.utils.timezone import now

class Feedback(models.Model):
    user = models.ForeignKey('registrationmodel', on_delete=models.CASCADE)  # Link to logged-in user
    rating = models.IntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)])  # 1-5 rating
    comment = models.TextField(blank=True, null=True)  # Optional comment
    created_at = models.DateTimeField(default=now)  # Auto timestamp

    def __str__(self):
        return f"{self.user.name} - {self.rating} Stars"

