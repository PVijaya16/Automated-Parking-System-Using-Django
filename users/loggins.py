from django.shortcuts import render,redirect, redirect, get_object_or_404
from django.contrib import messages
from .models import registrationmodel


def parkinglogincheck(request):
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

                return render(request, 'users/parkingentry.html', {'user': user})
            else:
                messages.error(request, 'Invalid password. Please try again.')
                return render(request, 'userlogin.html')
        except registrationmodel.DoesNotExist:
            messages.error(request, 'Email is not registered. Please sign up first.')
            return render(request, 'userlogin.html')
    return render(request, 'userlogin.html')
