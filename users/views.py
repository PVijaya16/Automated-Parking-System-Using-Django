from django.shortcuts import render,redirect, redirect, get_object_or_404
from django.contrib import messages
from .models import registrationmodel,openParkingSlot
from .forms import registrationmodelmodelform
from django.utils.timezone import now
from .models import openParkingSlot
import re
import qrcode
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
import os
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from datetime import datetime,timedelta 
from .models import CollegeParkingSlot
# from PIL import Image

# Create your views here.
#------------------------------------------------------------------main page-------------------------------------------------------

def basefunction(request):
    return render(request,'base.html')
    
# ----------------------------------------------------------------user login & logout---------------------------------------------------

def userlogin(request):
    return render(request,'userlogin.html') 

def userlogout(request):
    return render(request,'base.html')

#  ----------------------------------------------------------------user registration-----------------------------------------------------

def registercheck(request):
    if request.method == 'POST':
        form = registrationmodelmodelform(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            mobile = form.cleaned_data.get('mobile')
            if registrationmodel.objects.filter(email=email).exists():
                messages.warning(request, 'Email is already registered.')
            elif registrationmodel.objects.filter(mobile=mobile).exists():
                messages.warning(request, 'Mobile number is already registered.')
            else:
                instance = form.save(commit=False)
                instance.status = 'waiting'
                instance.save()
                messages.success(request, 'Account created successfully! Wait for activation by admin.')
                form = registrationmodelmodelform()  # Reset the form
                return render(request, 'studentregistration.html', {'form': form})
        else:
            print(form.errors)
            messages.warning(request, 'Please correct the errors below.')
    else:
        form = registrationmodelmodelform()
    return render(request, 'studentregistration.html', {'form': form})

# --------------------------------------------------------------------user login check-----------------------------------------------

def userlogincheck(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')
        try:
            user = registrationmodel.objects.get(email__iexact=email)
            print(f"Debug: Retrieved user status: {user.status}")
            if user.status.lower() == 'blocked':
                messages.error(request, 'Your account is blocked. Please contact our admin team.')
                return render(request, 'userlogin.html')
            if user.status.lower() != 'activated':
                messages.warning(request, 'Your account is not active. Please wait for admin approval.')
                return render(request, 'userlogin.html')
            if user.password == password:
                request.session['email'] = user.email
                request.session['name'] = user.name
                user.last_login = now()
                user.save()  
                print(f"Debug: Logged-in user email: {request.session['email']}")
                print(f"Debug: Logged-in user name: {request.session['name']}")
                print(f"Debug: Session data: {request.session.items()}")

                return render(request, 'users/userhome.html', {'user': user})
            else:
                messages.error(request, 'Invalid password. Please try again.')
                return render(request, 'userlogin.html')
        except registrationmodel.DoesNotExist:
            messages.error(request, 'Email is not registered. Please sign up first.')
            return render(request, 'userlogin.html')
    return render(request, 'userlogin.html')

# -------------------------------------------------------------user home & profile & profile update-------------------------------------------

def user_home(request):
    if 'email' not in request.session:
        return redirect('userlogin')
    email = request.session.get('email')
    user = registrationmodel.objects.get(email=email)
    return render(request, 'users/userhome.html', {'user': user})  

def user_profile(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, 'You need to log in first.')
        return redirect('userlogin')
    try:
        user = registrationmodel.objects.get(email=email)
        return render(request, 'users/profile.html', {'user': user})
    except registrationmodel.DoesNotExist:      
        return redirect('userlogin')

def update_profile(request):
    email = request.session.get('email')
    try:
        user = registrationmodel.objects.get(email=email)
    except registrationmodel.DoesNotExist:       
        return redirect('userlogin')
    if request.method == 'POST':
        form = registrationmodelmodelform(request.POST, instance=user)
        if form.is_valid():
            form.fields.pop('password', None)
            form.fields.pop('confirm_password', None)
            form.save()
            messages.success(request, 'Profile updated successfully! login with the new updated email.!')
            return redirect('userprofile')
        else:
            messages.warning(request, 'Please correct the errors below.')
    else:
        form = registrationmodelmodelform(instance=user)
        form.fields.pop('password', None)
        form.fields.pop('confirm_password', None)
    return render(request, 'users/profileupdate.html', {'form': form})


def parkingentry(request):
    if 'email' not in request.session:
        return redirect('userlogin')
    email = request.session.get('email')
    user = registrationmodel.objects.get(email=email)
    return render(request,'users/parkingentry.html')

def exitparking(request):
    if 'email' not in request.session:
        return redirect('userlogin')
    email = request.session.get('email')
    user = registrationmodel.objects.get(email=email)
    return render(request,'users/exitparking.html')           

# ----------------------------------------------------------------------open parking----------------------------------------------------
def openparkingfare(request):
    if 'email' not in request.session:
        return redirect('userlogin')
    email = request.session.get('email')
    user = registrationmodel.objects.get(email=email)
    return render(request,'openparking/openparkingsummary.html')

def open_parking(request):
    if request.method == "POST":
        category = request.POST.get('category')
        vehicle_type = request.POST.get('vehicle_type')
        vehicle_number = request.POST.get('vehicle_number')
        entry_time = now()
        print(f"Parking Request: Category={category}, Vehicle Type={vehicle_type}, Vehicle Number={vehicle_number}, Entry Time={entry_time}")
        # Find the first available parking slot
        slot = openParkingSlot.objects.filter(
            is_occupied=False,
            vehicle_type=vehicle_type,
            category=category
        ).order_by('slot_id').first()
        if slot:
            print(f"Allocating Slot: Slot ID={slot.slot_id}, Vehicle Type={slot.vehicle_type}, Category={slot.category}")
            # Render confirmation page with slot details
            return render(request, 'openparking/confirm_parking.html', {
                'slot': slot,
                'vehicle_number': vehicle_number,
                'entry_time': entry_time
            })
        else:
            print("No available slots.")
            # No available slots
            return render(request, 'openparking/slot_allocation_failed.html')
    return render(request, 'openparking/open_parking.html')

# ---------------------------------------------------------------------open parking confirm parking----------------------------------------------

def confirm_parking(request, slot_id):
    if request.method == "POST":
        vehicle_number = request.POST.get('vehicle_number')
        entry_time = datetime.now()
        # Retrieve the slot
        slot = openParkingSlot.objects.get(slot_id=slot_id)
        # Confirm the parking slot and mark it as occupied
        slot.is_occupied = True
        slot.vehicle_number = vehicle_number
        slot.entry_time = entry_time
        slot.save()
        # Generate QR Code data
        qr_data = (
            f"Slot Details:\n"
            f"Slot ID: {slot.slot_id}\n"
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
                f'Your parking lot : open parking.\n'
                f"Slot ID: {slot.slot_id}\n"
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
        return render(request, 'openparking/slot_allocation_success.html', {
            'slot': slot,
            'vehicle_number': vehicle_number,
            'entry_time': entry_time,
            'qr_code_url': f"{settings.MEDIA_URL}qr_codes/{qr_filename}",
            'email_sent': user_email is not None,  # Indicate if the email was sent
        })
    return redirect('open_parking')

# --------------------------------------------------------------------open parking checkout-----------------------------------------------------

def checkout_parking(request):
    if request.method == "POST":
        search_value = request.POST.get("search_value", "").strip()
        search_type = request.POST.get("search_type", "").strip()
        
        # Normalize vehicle number format
        search_value_normalized = re.sub(r"\s+", "", search_value)
        
        slot = None

        if search_type == "slot_id":
            slot = openParkingSlot.objects.filter(slot_id=search_value_normalized, is_occupied=True).first()
        elif search_type == "vehicle_number":
            slots = openParkingSlot.objects.filter(is_occupied=True)
            for s in slots:
                normalized_vehicle_number = re.sub(r"\s+", "", s.vehicle_number)
                if normalized_vehicle_number == search_value_normalized:
                    slot = s
                    break

        if slot:
            if slot.entry_time:
                exit_time = datetime.now()
                duration = exit_time - slot.entry_time
                duration_minutes = duration.total_seconds() / 60  # Convert to minutes

                # Default fare values for Regular vehicles
                base_fare = 20  
                extra_fare_per_30min = 10  

                # Adjust fare for 4-wheelers
                if slot.vehicle_type == "4W":  
                    base_fare = 40  
                    extra_fare_per_30min = 20  

                # Calculate the base fare for Regular vehicles
                if duration_minutes <= 30:
                    fare = base_fare  # Minimum charge for up to 30 minutes
                else:
                    extra_blocks = (duration_minutes - 30) // 30  
                    fare = base_fare + (extra_blocks * extra_fare_per_30min)

                # Apply VIP Fare Structure
                if slot.category == "VIP":
                    if duration_minutes <= 60:
                        fare = 100  # ₹100 for up to 1 hour
                    else:
                        # Calculate extra hours after the first hour
                        extra_hours = (duration_minutes - 60) // 60
                        fare = 100 + (extra_hours * 10)  # ₹10 for each extra hour

                # Debugging statements to check category and fare
                print(f"Vehicle Type: {slot.vehicle_type}")
                print(f"Slot Category: {slot.category}")
                print(f"Duration (in minutes): {duration_minutes}")
                print(f"Calculated Fare: ₹{fare}")

                # Store details in session (but **DO NOT** mark slot as available yet)
                request.session['slot_id'] = slot.slot_id
                request.session['vehicle_number'] = slot.vehicle_number
                request.session['entry_time'] = slot.entry_time.strftime('%Y-%m-%d %H:%M:%S')
                request.session['exit_time'] = exit_time.strftime('%Y-%m-%d %H:%M:%S')
                request.session['fare'] = fare

                return render(request, 'openparking/checkout_success.html', {
                    'slot': slot,
                    'vehicle_number': slot.vehicle_number,
                    'entry_time': slot.entry_time,
                    'exit_time': exit_time,
                    'fare': fare,
                    'duration_minutes': int(duration_minutes),
                    'email_sent': False
                })
            else:
                return render(request, 'openparking/checkout_failed.html', {
                    'error': 'Entry time not set for this parking slot.'
                })
        else:
            return render(request, 'openparking/checkout_failed.html', {
                'error': f"No slot found for {search_value}. Please try again."
            })

    return render(request, 'openparking/checkout_parking.html')



# --------------------------------------------------------------------open parking confirm payment-----------------------------------------------------

def confirm_payment(request, slot_id):
    slot = openParkingSlot.objects.get(slot_id=slot_id)

    if request.method == "POST":
        # Retrieve session details
        vehicle_number = request.session.get('vehicle_number', 'N/A')
        entry_time = request.session.get('entry_time', 'N/A')
        exit_time = request.session.get('exit_time', 'N/A')
        fare = request.session.get('fare', 0)

        # **Now** mark the slot as available (after payment confirmation)
        slot.is_occupied = False
        slot.vehicle_number = None
        slot.entry_time = None
        slot.exit_time = None  # Optional: Keep it for records
        slot.payment_status = True
        slot.save()

        # Send confirmation email
        user_email = request.session.get('email')  
        if user_email:
            email_subject = "Payment Confirmation & Parking Checkout Details"
            email_message = (
                f"Dear User,\n\nYour parking session has been successfully checked out and payment confirmed.\n\n"
                f"Slot Details:\n"
                f'Your parking lot: Open Parking.\n'
                f"Slot ID: {slot.slot_id}\n"
                f"Vehicle Number: {vehicle_number}\n"
                f"Entry Time: {entry_time}\n"
                f"Exit Time: {exit_time}\n"
                f"Fare: ₹{fare}\n\n"
                f"Thank you for using our service.\n\n"
                f"Please note: This is a no-reply email. Do not reply to this message.\n\n"
                f"Regards,\nParking Management Team"
            )
            email = EmailMessage(
                email_subject,
                email_message,
                'No Reply - Parking Checkout Service <' + settings.DEFAULT_FROM_EMAIL + '>',
                [user_email],
            )
            email.send()

        return render(request, 'openparking/payment_success.html', {'slot': slot})

    return render(request, 'openparking/confirm_payment.html', {'slot': slot})

# ----------------------------------------------------------------------- College Parking -----------------------------------------------------
def collegefare(request):
    if 'email' not in request.session:
        return redirect('userlogin')
    email = request.session.get('email')
    user = registrationmodel.objects.get(email=email)
    return render(request,'collegeparking/faresummary.html')

def collegeparking(request):
    if request.method == "POST":
        category = request.POST.get('category')
        vehicle_type = request.POST.get('vehicle_type')
        vehicle_number = request.POST.get('vehicle_number')
        entry_time = now()
        print(f"Parking Request: Category={category}, Vehicle Type={vehicle_type}, Vehicle Number={vehicle_number}, Entry Time={entry_time}")
        # Find the first available parking slot
        slot = CollegeParkingSlot.objects.filter(
            is_occupied=False,
            vehicle_type=vehicle_type,
            category=category
        ).order_by('slot_id').first()
        if slot:
            print(f"Allocating Slot: Slot ID={slot.slot_id}, Vehicle Type={slot.vehicle_type}, Category={slot.category}")
            # Render confirmation page with slot details
            return render(request, 'collegeparking/confirm_parking.html', {
                'slot': slot,
                'vehicle_number': vehicle_number,
                'entry_time': entry_time
            })
        else:
            print("No available slots.")
            # No available slots
            return render(request, 'collegeparking/slot_allocation_failed.html')
    return render(request, 'collegeparking/collegeparking.html')

# --------------------------------------------------------------------college parking confirm parking-----------------------------------------------------

def confirmcollegeparking(request, slot_id):
    if request.method == "POST":
        vehicle_number = request.POST.get('vehicle_number')
        entry_time = datetime.now()
        # Retrieve the slot
        slot = CollegeParkingSlot.objects.get(slot_id=slot_id)
        # Confirm the parking slot and mark it as occupied
        slot.is_occupied = True
        slot.vehicle_number = vehicle_number
        slot.entry_time = entry_time
        slot.save()
        # Generate QR Code data
        qr_data = (
            f"Slot Details:\n"
            f"Slot ID: {slot.slot_id}\n"
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
                f'Your parking lot : college parking.\n'
                f"Slot Details:\n"
                f"Slot ID: {slot.slot_id}\n"
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
        return render(request, 'collegeparking/slot_allocation_success.html', {
            'slot': slot,
            'vehicle_number': vehicle_number,
            'entry_time': entry_time,
            'qr_code_url': f"{settings.MEDIA_URL}qr_codes/{qr_filename}",
            'email_sent': user_email is not None,  # Indicate if the email was sent
        })
    return redirect('open_parking')

def collegecheckoutparking(request):
    if request.method == "POST":
        try:
            search_value = request.POST.get("search_value", "").strip()
            search_type = request.POST.get("search_type", "")
            # Normalize the search value
            search_value_normalized = re.sub(r"\s+", "", search_value)
            # Initialize slot to None
            slot = None
            # Handle search by slot ID
            if search_type == "slot_id":
                slot = CollegeParkingSlot.objects.filter(slot_id=str(search_value_normalized)).first()
                if slot:
                    if not slot.is_occupied:
                        return render(request, 'collegeparking/checkout_failed.html', {
                            'error': f"Slot {search_value} is not currently occupied."
                        })
            # Handle search by vehicle number
            elif search_type == "vehicle_number":
                slots = CollegeParkingSlot.objects.filter(is_occupied=True)
                for s in slots:
                    normalized_vehicle_number = re.sub(r"\s+", "", s.vehicle_number)
                    if normalized_vehicle_number == search_value_normalized:
                        slot = s
                        break
            else:
                return render(request, 'collegeparking/checkout_failed.html', {
                    'error': 'Invalid search type. Please try again.'
                })
            if slot:
                if slot.entry_time:
                    # Calculate duration and fare
                    exit_time = datetime.now()
                    duration = exit_time - slot.entry_time
                    duration_minutes = duration.total_seconds() / 60
                    
                    # Fare calculation logic
                    if slot.category == "Student" or slot.category == "Faculty":
                        fare = 0  # No fare for students and faculty
                    else:  # Visitor category
                        base_fare = 10 if slot.vehicle_type == "2W" else 15
                        extra_fare = 0
                        if duration_minutes > 60:
                            extra_fare = ((duration_minutes - 60) // 60) * (10 if slot.vehicle_type == "2W" else 15)
                        fare = base_fare + extra_fare
                    
                    # Mark payment as pending, but keep the slot occupied
                    slot.exit_time = exit_time
                    slot.payment_status = False  # Payment not yet confirmed
                    slot.save()
                    
                    # Save session data
                    request.session['slot_id'] = slot.slot_id
                    request.session['vehicle_number'] = slot.vehicle_number
                    request.session['entry_time'] = slot.entry_time.strftime('%Y-%m-%d %H:%M:%S')
                    request.session['exit_time'] = exit_time.strftime('%Y-%m-%d %H:%M:%S')
                    request.session['fare'] = fare
                    
                    # Render success page
                    return render(request, 'collegeparking/checkout_success.html', {
                        'slot': slot,
                        'vehicle_number': slot.vehicle_number,
                        'entry_time': slot.entry_time,
                        'exit_time': exit_time,
                        'fare': fare,
                        'duration_minutes': int(duration_minutes),
                        'email_sent': False
                    })
                else:
                    return render(request, 'collegeparking/checkout_failed.html', {
                        'error': 'Entry time not set for this parking slot.'
                    })
            else:
                return render(request, 'collegeparking/checkout_failed.html', {
                    'error': f"No parking slot found for {search_value}. Please try again."
                })
        except Exception as e:
            return render(request, 'collegeparking/checkout_failed.html', {
                'error': 'An unexpected error occurred. Please try again later.' 
            })
    return render(request, 'collegeparking/checkoutparking.html')


def collegeconfirmpayment(request, slot_id):
    try:
        # Retrieve the slot based on the slot ID
        slot = CollegeParkingSlot.objects.get(slot_id=slot_id)
        if request.method == "POST":
            # Retrieve session details
            vehicle_number = request.session.get('vehicle_number', 'N/A')
            entry_time = request.session.get('entry_time', 'N/A')
            exit_time = request.session.get('exit_time', 'N/A')
            fare = request.session.get('fare', 0)
            # Mark the slot as available only after payment
            slot.is_occupied = False
            slot.vehicle_number = None
            slot.entry_time = None
            slot.exit_time = None
            slot.payment_status = True  # Payment confirmed
            slot.save()
            # Send confirmation email
            user_email = request.session.get('email')  # Assuming user email is stored in session
            if user_email:
                email_subject = "Payment Confirmation & Parking Checkout Details"
                email_message = (
                    f"Dear User,\n\nYour parking session has been successfully checked out and payment confirmed.\n\n"
                    f"Slot Details:\n"
                    f"Slot ID: {slot.slot_id}\n"
                    f"Vehicle Number: {vehicle_number}\n"
                    f"Entry Time: {entry_time}\n"
                    f"Exit Time: {exit_time}\n"
                    f"Fare: ₹{fare}\n\n"
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
            return render(request, 'collegeparking/payment_success.html', {'slot': slot})

        return render(request, 'collegeparking/confirm_payment.html', {'slot': slot})
    except CollegeParkingSlot.DoesNotExist:
        return render(request, 'collegeparking/checkout_failed.html', {
            'error': f"Slot with ID {slot_id} does not exist."
        })



from .forms import FeedbackForm
def submit_feedback(request):
    print("Session Data:", request.session.items())  # Debugging session data

    if 'email' not in request.session:
        messages.error(request, "You must be logged in to submit feedback.")
        return redirect("userlogin")  # Redirect to login page if session expired

    # Fetch the logged-in user
    email = request.session.get("email")
    print(f"Retrieved Email from Session: {email}")  # Debugging session retrieval

    try:
        user = registrationmodel.objects.get(email=email)
    except registrationmodel.DoesNotExist:
        messages.error(request, "User not found in registration records.")
        return redirect("userlogin")

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return render(request, "users/feedback_form.html", {"form": form}) # Redirect to dashboard
    else:
        form = FeedbackForm()

    return render(request, "users/feedback_form.html", {"form": form})


