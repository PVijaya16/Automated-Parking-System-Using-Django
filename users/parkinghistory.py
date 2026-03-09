from django.shortcuts import render
from .models import openParkingSlot

# def parking_history(request):
#     # Fetch all occupied parking slots with entry and exit times
#     parking_slots = openParkingSlot.objects.filter(is_occupied=True)

#     parking_data = []
    
#     for slot in parking_slots:
#         # Ensure entry_time and exit_time are present
#         if slot.entry_time and slot.exit_time:
#             duration = slot.exit_time - slot.entry_time
#             duration_minutes = duration.total_seconds() / 60  # Convert to minutes
#         else:
#             duration_minutes = None  # If no exit time, set duration as None

#         # Prepare data to pass to the template
#         parking_data.append({
#             'slot_id': slot.slot_id,
#             'vehicle_number': slot.vehicle_number,
#             'vehicle_type': slot.vehicle_type,
#             'category': slot.category,
#             'entry_time': slot.entry_time.strftime('%Y-%m-%d %H:%M:%S') if slot.entry_time else None,
#             'exit_time': slot.exit_time.strftime('%Y-%m-%d %H:%M:%S') if slot.exit_time else None,
#             'duration_minutes': int(duration_minutes) if duration_minutes else None,
#         })

#     return render(request, 'parkinghistory/parking_history.html', {
#         'parking_data': parking_data,
#     })

def parking_history(request):
    # Fetch the different types of parked vehicles (is_occupied=True)
    regular_2w = openParkingSlot.objects.filter(is_occupied=True, vehicle_type='2W', category='Regular')
    regular_4w = openParkingSlot.objects.filter(is_occupied=True, vehicle_type='4W', category='Regular')
    vip_2w = openParkingSlot.objects.filter(is_occupied=True, vehicle_type='2W', category='VIP')
    vip_4w = openParkingSlot.objects.filter(is_occupied=True, vehicle_type='4W', category='VIP')

    # Debugging print statements
    print(f"Regular 2W: {regular_2w.count()} vehicles")
    print(f"Regular 4W: {regular_4w.count()} vehicles")
    print(f"VIP 2W: {vip_2w.count()} vehicles")
    print(f"VIP 4W: {vip_4w.count()} vehicles")

    # Function to format the vehicle status based on exit time
    def get_vehicle_status(exit_time):
        if exit_time:
            return 'Exited'
        else:
            return 'Not Exited'

    # Prepare the data for each table
    def get_parked_data(slots):
        parked_data = []
        for slot in slots:
            parked_data.append({
                'slot_id': slot.slot_id,
                'vehicle_number': slot.vehicle_number,
                'vehicle_type': slot.vehicle_type,
                'category': slot.category,
                'entry_time': slot.entry_time.strftime('%Y-%m-%d %H:%M:%S') if slot.entry_time else None,
                'status': get_vehicle_status(slot.exit_time),  # Add the status
            })
        return parked_data

    # Get parked data for each category
    regular_2w_data = get_parked_data(regular_2w)
    regular_4w_data = get_parked_data(regular_4w)
    vip_2w_data = get_parked_data(vip_2w)
    vip_4w_data = get_parked_data(vip_4w)

    return render(request, 'parkinghistory/parking_history.html', {
        'regular_2w_data': regular_2w_data,
        'regular_4w_data': regular_4w_data,
        'vip_2w_data': vip_2w_data,
        'vip_4w_data': vip_4w_data,
    })




from django.shortcuts import render
from .models import CollegeParkingSlot

def college_parking_history(request):
    # Faculty Parking
    faculty_2w = CollegeParkingSlot.objects.filter(is_occupied=True, category="Faculty", vehicle_type="2W").order_by('-entry_time')
    faculty_4w = CollegeParkingSlot.objects.filter(is_occupied=True, category="Faculty", vehicle_type="4W").order_by('-entry_time')

    # Student Parking
    student_2w = CollegeParkingSlot.objects.filter(is_occupied=True, category="Student", vehicle_type="2W").order_by('-entry_time')
    student_4w = CollegeParkingSlot.objects.filter(is_occupied=True, category="Student", vehicle_type="4W").order_by('-entry_time')

    # Visitor Parking
    visitor_2w = CollegeParkingSlot.objects.filter(is_occupied=True, category="Visitor", vehicle_type="2W").order_by('-entry_time')
    visitor_4w = CollegeParkingSlot.objects.filter(is_occupied=True, category="Visitor", vehicle_type="4W").order_by('-entry_time')

    return render(request, 'parkinghistory/collegeparking_history.html', {
        'faculty_2w': faculty_2w, 'faculty_4w': faculty_4w,
        'student_2w': student_2w, 'student_4w': student_4w,
        'visitor_2w': visitor_2w, 'visitor_4w': visitor_4w
    })


from django.shortcuts import render
from .models import HospitalParkingSlot

def hospital_parking_history(request):
    # Currently parked vehicles categorized by Category and Vehicle Type
    staff_2w = HospitalParkingSlot.objects.filter(is_occupied=True, category="Staff", vehicle_type="2W").order_by('-entry_time')
    staff_4w = HospitalParkingSlot.objects.filter(is_occupied=True, category="Staff", vehicle_type="4W").order_by('-entry_time')

    patient_2w = HospitalParkingSlot.objects.filter(is_occupied=True, category="Patient", vehicle_type="2W").order_by('-entry_time')
    patient_4w = HospitalParkingSlot.objects.filter(is_occupied=True, category="Patient", vehicle_type="4W").order_by('-entry_time')

    vip_2w = HospitalParkingSlot.objects.filter(is_occupied=True, category="VIP", vehicle_type="2W").order_by('-entry_time')
    vip_4w = HospitalParkingSlot.objects.filter(is_occupied=True, category="VIP", vehicle_type="4W").order_by('-entry_time')



    return render(request, 'parkinghistory/hospital_parking_history.html', {
        'staff_2w': staff_2w, 'staff_4w': staff_4w,
        'patient_2w': patient_2w, 'patient_4w': patient_4w,
        'vip_2w': vip_2w, 'vip_4w': vip_4w,
    
    })
