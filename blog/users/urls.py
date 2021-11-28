from django.urls import path
from users.views import RegisterView,ImageCodeView
from users.views import SmsCodeView,LoginView
from users.views import LogoutView,ForgetPasswordView
urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),



    path('imagecode/',ImageCodeView.as_view(),name='imagecode'),



    path('smscode/',SmsCodeView.as_view(),name='smscode'),



    path('login/',LoginView.as_view(),name='login'),



    path('logout/',LogoutView.as_view(),name='logout'),



    path('forgetpassword/',ForgetPasswordView.as_view(),name='forgetpassword'),
]


