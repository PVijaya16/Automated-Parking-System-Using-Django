from django.core.management.base import BaseCommand
from users.models import openParkingSlot

class Command(BaseCommand):
    help = 'Populate the database with 1000 parking slots'

    def handle(self, *args, **kwargs):
        # Clear existing slots to avoid duplication
        openParkingSlot.objects.all().delete()

        # Create regular slots: 400 for 2-wheelers, 400 for 4-wheelers
        for i in range(400):
            openParkingSlot.objects.create(vehicle_type='2W', category='Regular')
            openParkingSlot.objects.create(vehicle_type='4W', category='Regular')

        # Create VIP slots: 100 for 2-wheelers, 100 for 4-wheelers
        for i in range(100):
            openParkingSlot.objects.create(vehicle_type='2W', category='VIP')
            openParkingSlot.objects.create(vehicle_type='4W', category='VIP')

        self.stdout.write(self.style.SUCCESS('Successfully created 1000 parking slots!'))
