from django.shortcuts import render, redirect
from django.utils.timezone import now
from .models import HospitalParkingSlot
from .views import *
import os
import qrcode
from io import BytesIO
from datetime import datetime
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, redirect
from .models import HospitalParkingSlot


def hospitalfare(request):
    if 'email' not in request.session:
        return redirect('userlogin')
    email = request.session.get('email')
    user = registrationmodel.objects.get(email=email)
    return render(request,'hospitalparking/faresummary.html')

def hospitalparkigentry(request):
    if request.method == "POST":
        category = request.POST.get('category')
        vehicle_type = request.POST.get('vehicle_type')
        vehicle_number = request.POST.get('vehicle_number')
        entry_time = now()

        print(f"Parking Request: Category={category}, Vehicle Type={vehicle_type}, Vehicle Number={vehicle_number}, Entry Time={entry_time}")

        # Find the first available slot across all floors
        slot = HospitalParkingSlot.objects.filter(
            is_occupied=False,
            vehicle_type=vehicle_type,
            category=category
        ).order_by('floor', 'slot_id').first()

        if slot:
            print(f"Auto Allocated Slot: {slot.slot_id} on Floor {slot.floor}")

            # Render confirmation page with slot details
            return render(request, 'hospitalparking/confirmhopitalparking.html', {
                'slot': slot,
                'vehicle_number': vehicle_number,
                'entry_time': entry_time
            })
        else:
            print("No available slots.")
            # No available slots
            return render(request, 'hospitalparking/slot_allocation_failed.html')

    return render(request, 'hospitalparking/hoSpitalparking.html')



def hospital_confirm_parking(request, slot_id):
    if request.method == "POST":
        vehicle_number = request.POST.get('vehicle_number')
        entry_time = datetime.now()

        # Retrieve the slot
        slot = HospitalParkingSlot.objects.get(slot_id=slot_id)

        # Confirm the parking slot and mark it as occupied
        slot.is_occupied = True
        slot.vehicle_number = vehicle_number
        slot.entry_time = entry_time
        slot.save()

        # Generate QR Code data
        qr_data = (
            f"Slot Details:\n"
            f"Slot ID: {slot.slot_id}\n"
            f"Floor Number: {slot.floor}\n"  # Added Floor Number
            f"Category: {slot.category}\n"
            f"Vehicle Type: {slot.vehicle_type}\n"
            f"Vehicle Number: {vehicle_number}\n"
            f"Entry Time: {entry_time.strftime('%b. %d, %Y, %I:%M %p')}\n"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")

        # Save QR code to the media folder
        qr_folder_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(qr_folder_path, exist_ok=True)  # Create folder if it doesn't exist
        qr_filename = f"parking_qr_{slot.slot_id}.png"
        qr_image_path = os.path.join(qr_folder_path, qr_filename)
        qr_img.save(qr_image_path)

        # Prepare the QR code in Base64 format for email attachment
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        # Send email with parking details
        user_email = request.session.get('email')  # Assuming user email is stored in session
        if user_email:
            email_subject = "Your Parking Slot Confirmation"
            email_message = (
                f"Dear User,\n\nYour parking slot has been successfully confirmed.\n\n"
                f"Slot Details:\n"
                f"Your parking lot: Hospital Parking.\n"
                f"Slot ID: {slot.slot_id}\n"
                f"Floor Number: {slot.floor}\n"  # Added Floor Number
                f"Category: {slot.category}\n"
                f"Vehicle Type: {slot.vehicle_type}\n"
                f"Vehicle Number: {vehicle_number}\n"
                f"Entry Time: {entry_time.strftime('%b. %d, %Y, %I:%M %p')}\n\n"
                f"Thank you for using our service.\n\n"
                f"Please note: This is a no-reply email. Do not reply to this message.\n\n"
                f"Regards,\nParking Management Team"
            )

            # Attach QR code as an email attachment
            email = EmailMessage(
                email_subject,
                email_message,
                'No Reply - Parking Management Service <' + settings.DEFAULT_FROM_EMAIL + '>',
                [user_email],
            )
            email.attach('parking_qr_code.png', qr_buffer.getvalue(), 'image/png')
            email.send()

        # Render the success page
        return render(request, 'hospitalparking/slot_allocation_success.html', {
            'slot': slot,
            'vehicle_number': vehicle_number,
            'entry_time': entry_time,
            'qr_code_url': f"{settings.MEDIA_URL}qr_codes/{qr_filename}",
            'email_sent': user_email is not None,  # Indicate if the email was sent
        })

    return redirect('hospitalparkigentry')



import re
from datetime import datetime
from django.shortcuts import render
from .models import HospitalParkingSlot

def hospital_checkout_parking(request):
    if request.method == "POST":
        try:
            search_value = request.POST.get("search_value", "").strip()
            search_type = request.POST.get("search_type", "")
            search_value_normalized = re.sub(r"\s+", "", search_value)
            slot = None

            # Handle search by slot ID
            if search_type == "slot_id":
                slot = HospitalParkingSlot.objects.filter(slot_id=search_value_normalized).first()
                if slot and not slot.is_occupied:
                    return render(request, 'hospitalparking/checkout_failed.html', {
                        'error': f"Slot {search_value} is not currently occupied."
                    })
            
            # Handle search by vehicle number
            elif search_type == "vehicle_number":
                slots = HospitalParkingSlot.objects.filter(is_occupied=True)
                for s in slots:
                    if s.vehicle_number and re.sub(r"\s+", "", s.vehicle_number) == search_value_normalized:
                        slot = s
                        break
            else:
                return render(request, 'hospitalparking/checkout_failed.html', {
                    'error': 'Invalid search type. Please try again.'
                })

            if slot:
                if slot.entry_time:
                    exit_time = datetime.now()
                    duration = exit_time - slot.entry_time
                    duration_hours = duration.total_seconds() / 3600  # Convert to hours

                    # Default fare is 0 for Staff and Patients
                    if slot.category in ["Staff", "Patient"]:
                        fare = 0
                    else:  # VIP category
                        base_fare = 40 if slot.vehicle_type == "4W" else 60
                        extra_fare = 0
                        if duration_hours > 1:
                            extra_fare = ((duration_hours - 1) // 1) * 20  # ₹20 per extra hour
                        fare = base_fare + extra_fare

                    # Mark payment as pending, but keep the slot occupied
                    slot.exit_time = exit_time
                    slot.payment_status = False  # Payment not yet confirmed
                    slot.save()

                    # Store session data for payment processing
                    request.session['slot_id'] = slot.slot_id
                    request.session['vehicle_number'] = slot.vehicle_number
                    request.session['entry_time'] = slot.entry_time.strftime('%Y-%m-%d %H:%M:%S')
                    request.session['exit_time'] = exit_time.strftime('%Y-%m-%d %H:%M:%S')
                    request.session['fare'] = fare

                    return render(request, 'hospitalparking/checkout_success.html', {
                        'slot': slot,
                        'vehicle_number': slot.vehicle_number,
                        'entry_time': slot.entry_time,
                        'exit_time': exit_time,
                        'fare': fare,
                        'duration_hours': int(duration_hours),
                        'email_sent': False
                    })
                else:
                    return render(request, 'hospitalparking/checkout_failed.html', {
                        'error': 'Entry time not set for this parking slot.'
                    })
            else:
                return render(request, 'hospitalparking/checkout_failed.html', {
                    'error': f"No parking slot found for {search_value}. Please try again."
                })
        except Exception as e:
            return render(request, 'hospitalparking/checkout_failed.html', {
                'error': 'An unexpected error occurred. Please try again later.' 
            })
    
    return render(request, 'hospitalparking/hospitalcheckout.html')




def hospitalconfirmpayment(request, slot_id):
    try:
        slot = HospitalParkingSlot.objects.get(slot_id=slot_id)

        if request.method == "POST":
            vehicle_number = request.session.get('vehicle_number', 'N/A')
            entry_time = request.session.get('entry_time', 'N/A')
            exit_time = request.session.get('exit_time', 'N/A')
            fare = request.session.get('fare', 0)

            # 🚨 Skip payment if Faculty or Student 🚨
            if slot.category in ["staff", "patient"]:
                slot.payment_status = True  # Mark as paid (even though free)
            else:
                slot.payment_status = True  # Mark payment as completed

            # Free up the slot
            slot.is_occupied = False
            slot.vehicle_number = None
            slot.entry_time = None
            slot.exit_time = None
            slot.save()

            # Send confirmation email
            user_email = request.session.get('email')
            if user_email:
                email_subject = "Payment Confirmation & Parking Checkout Details"
                email_message = (
                    f"Dear User,\n\nYour parking session has been successfully checked out.\n\n"
                    f"Slot Details:\n"
                    f"Slot ID: {slot.slot_id}\n"
                    f"Vehicle Number: {vehicle_number}\n"
                    f"Entry Time: {entry_time}\n"
                    f"Exit Time: {exit_time}\n"
                    f"Fare: ₹{fare} (Free for Faculty & Students)\n\n"
                    f"Thank you for using our service.\n\n"
                    f"Regards,\nParking Management Team"
                )

                email = EmailMessage(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user_email],
                )
                email.send()

            return render(request, 'hospitalparking/payment_success.html', {'slot': slot})

        return render(request, 'hospitalparking/confirm_payment.html', {'slot': slot})

    except CollegeParkingSlot.DoesNotExist:
        return render(request, 'hospitalparking/checkout_failed.html', {
            'error': f"Slot with ID {slot_id} does not exist."
        })


