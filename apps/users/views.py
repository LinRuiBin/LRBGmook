from django.shortcuts import render
from django.http.response import HttpResponse
from  django.contrib.auth import  authenticate, login
from  django.contrib.auth.backends import ModelBackend
from  .models import UserProfile
from django.db.models import Q
from django.views.generic.base import View
from .form import LoginForm,RegisterForm
from utils.email_send import send_register_email
from django.contrib.auth.hashers import make_password
# Create your views here.

class LoginView(View):
    def get(self,request):
        return render(request , 'login.html' , {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username' , '')
            user_pwd = request.POST.get('password' , '')
            user = authenticate(username=user_name , password=user_pwd)
            if user is not None:
                login(request , user)
                return render(request , 'index.html' , {})
            else:
                return render(request , 'login.html' , {'msg': "用户名或密码错误"})
        else: return render(request , 'login.html' , {'msg': "用户名或密码错误","login_form":login_form})

class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class RegisterView(View):
    def get(self , request):
        register_form = RegisterForm()
        return render(request , "register.html" , {'register_form': register_form})

    def post(self , request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email" , "")
            if UserProfile.objects.filter(email=user_name):
                return render(request , "register.html" , {"register_form": register_form , "msg": "用户已经存在"})
            pass_word = request.POST.get("password" , "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            send_register_email(user_name , "register")
            return render(request , "login.html")
        else:
            return render(request , "register.html" , {"register_form": register_form})