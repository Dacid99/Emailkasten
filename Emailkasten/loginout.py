from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json 

@csrf_exempt    #only for debug!
def login_view(request):
    if request.method =='POST':
        data = json.loads(request.body)
        userName = data.get('username')
        userPassword = data.get('password')
        remember = data.get('remember', False)
        user = authenticate(request, userName, userPassword)
        if user is not None:
            login(request, user)
            if remember:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            else:
                request.session.set_expiry(0)
            return JsonResponse({'message': 'Login successfully'}, status = 200)
        else:
            return JsonResponse({'message': 'Invalid credentials'}, status = 401)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status = 405)
    

@csrf_exempt   #only for debug!
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful'}, status = 200)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status = 405)