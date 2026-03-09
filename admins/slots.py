from django.shortcuts import render, redirect




def penparkingslots(request):
    user_name = request.session.get('user_name', None)
    print(f"AdminHome: Logged-in User = {user_name}")  
    return render(request, 'admins/openparkingslots.html',{'user_name': user_name})

def collegeparking(request):
    user_name = request.session.get('user_name', None)
    print(f"AdminHome: Logged-in User = {user_name}")  
    return render(request, 'admins/collegeparking.html',{'user_name': user_name})


def hospitalparkingslots(request):
    user_name = request.session.get('user_name', None)
    print(f"AdminHome: Logged-in User = {user_name}")  
    return render(request, 'admins/hospitalparkingslots.html',{'user_name': user_name})            

