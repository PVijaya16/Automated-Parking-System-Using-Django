from django.core.management.base import BaseCommand
from users.models import CollegeParkingSlot  # Adjust based on your app name

class Command(BaseCommand):
    help = 'Create parking slots for students, faculty, and visitors'

    def handle(self, *args, **kwargs):
        # Helper function to generate slot_id
        def generate_slot_id(category, count):
            return f"{category[:2].upper()}{str(count).zfill(4)}"

        # Initialize counters for each category
        student_count_2w = 1
        student_count_4w = 601
        faculty_count_2w = 1001
        faculty_count_4w = 1101
        visitor_count_2w = 1201
        visitor_count_4w = 1351

        # Create 600 slots for 2-Wheelers and 400 slots for 4-Wheelers for Students
        for i in range(1, 601):
            slot_id = generate_slot_id('Student', student_count_2w)
            CollegeParkingSlot.objects.create(
                vehicle_type='2W',
                category='Student',
                is_occupied=False,
                slot_id=slot_id,
            )
            student_count_2w += 1

        for i in range(601, 1001):
            slot_id = generate_slot_id('Student', student_count_4w)
            CollegeParkingSlot.objects.create(
                vehicle_type='4W',
                category='Student',
                is_occupied=False,
                slot_id=slot_id,
            )
            student_count_4w += 1

        # Create 200 slots for Faculty: 100 for 2-Wheelers and 100 for 4-Wheelers
        for i in range(1001, 1101):
            slot_id = generate_slot_id('Faculty', faculty_count_2w)
            CollegeParkingSlot.objects.create(
                vehicle_type='2W',
                category='Faculty',
                is_occupied=False,
                slot_id=slot_id,
            )
            faculty_count_2w += 1

        for i in range(1101, 1201):
            slot_id = generate_slot_id('Faculty', faculty_count_4w)
            CollegeParkingSlot.objects.create(
                vehicle_type='4W',
                category='Faculty',
                is_occupied=False,
                slot_id=slot_id,
            )
            faculty_count_4w += 1

        # Create 300 slots for Visitors: 150 for 2-Wheelers and 150 for 4-Wheelers
        for i in range(1201, 1351):
            slot_id = generate_slot_id('Visitor', visitor_count_2w)
            CollegeParkingSlot.objects.create(
                vehicle_type='2W',
                category='Visitor',
                is_occupied=False,
                slot_id=slot_id,
            )
            visitor_count_2w += 1

        for i in range(1351, 1501):
            slot_id = generate_slot_id('Visitor', visitor_count_4w)
            CollegeParkingSlot.objects.create(
                vehicle_type='4W',
                category='Visitor',
                is_occupied=False,
                slot_id=slot_id,
            )
            visitor_count_4w += 1

        # Success message
        self.stdout.write(self.style.SUCCESS('Successfully created 1500 parking slots with custom slot IDs!'))
