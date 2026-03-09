from django.core.management.base import BaseCommand
from users.models import HospitalParkingSlot


class Command(BaseCommand):
    help = "Create hospital parking slots for floors 1, 2, and 3"

    def handle(self, *args, **options):
        # Define the configuration for floors and categories
        floors = {
            1: {'categories': ['Patient'], 'slots_per_category': 500},
            2: {'categories': ['Patient'], 'slots_per_category': 500},
            3: {'categories': ['Staff', 'VIP'], 'slots_per_category': 250},  # 250 slots for each category
        }

        vehicle_types = ['2W', '4W']  # Two types of vehicles

        # Function to get the last used slot_id for a given vehicle type on a floor
        def get_last_slot_id(vehicle_type, floor):
            try:
                # Get the last slot for the given vehicle type and floor
                last_slot = HospitalParkingSlot.objects.filter(vehicle_type=vehicle_type, floor=floor).order_by('-slot_id').first()
                return int(last_slot.slot_id.split('-')[2]) if last_slot else 0
            except HospitalParkingSlot.DoesNotExist:
                return 0

        # Loop through each floor and create the slots
        for floor, config in floors.items():
            categories = config['categories']
            slots_per_category = config['slots_per_category'] // len(vehicle_types)  # Divide equally for 2W and 4W

            for category in categories:
                # Get the last slot ID for 2W and 4W vehicles on the current floor
                last_2w_slot = get_last_slot_id('2W', floor)
                last_4w_slot = get_last_slot_id('4W', floor)

                # Set counters based on vehicle type
                if floor == 1:
                    slot_counter_2w = 1  # Start 2W slots from 001 for floor 1
                    slot_counter_4w = 251  # Start 4W slots from 251 for floor 1
                elif floor == 2:
                    slot_counter_2w = 1  # Start 2W slots from 001 for floor 2
                    slot_counter_4w = 251  # Start 4W slots from 251 for floor 2
                else:
                    slot_counter_2w = 1  # Start 2W slots from 001 for floor 3
                    slot_counter_4w = 251  # Start 4W slots from 251 for floor 3

                for vehicle_type in vehicle_types:
                    if vehicle_type == '2W':
                        counter = slot_counter_2w
                    else:
                        counter = slot_counter_4w

                    for i in range(1, slots_per_category + 1):
                        # Adjust slot ID generation based on vehicle type and floor
                        slot_id = f"{category[:1].upper()}{floor}-{vehicle_type}-{str(counter).zfill(3)}"

                        # Check if the slot_id already exists, if so, increment the counter
                        while HospitalParkingSlot.objects.filter(slot_id=slot_id).exists():
                            counter += 1  # Increment counter to avoid duplication
                            slot_id = f"{category[:1].upper()}{floor}-{vehicle_type}-{str(counter).zfill(3)}"

                        # Create the parking slot entry
                        slot = HospitalParkingSlot(
                            slot_id=slot_id,
                            vehicle_type=vehicle_type,
                            category=category,
                            is_occupied=False,
                            floor=floor
                        )
                        slot.save()

                        # Increment the counter for the next slot
                        if vehicle_type == '2W':
                            slot_counter_2w = counter + 1
                        else:
                            slot_counter_4w = counter + 1

                        self.stdout.write(f"Created: Floor {floor} | Slot ID {slot_id} | {vehicle_type} | {category}")

        self.stdout.write("Hospital parking slots created successfully.")
