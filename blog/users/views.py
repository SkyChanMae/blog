from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse

# Create your views here.
from django.views import View
from django.http.response import HttpResponseBadRequest
import re
from users.models import User
from django.db import DatabaseError
import logging
logger=logging.getLogger('django')

class RegisterView(View):

    def get(self,request):

        return render(request,'register.html')

    def post(self,request):

        mobile=request.POST.get('mobile')
        password=request.POST.get('password')
        password2=request.POST.get('password2')
        smscode=request.POST.get('sms_code')

        if not all([mobile,password,password2,smscode]):
            return HttpResponseBadRequest('缺少必要的参数')

        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return HttpResponseBadRequest('手机号不符合规则')

        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):
            return HttpResponseBadRequest('请输入正确的8-20位密码，数字和字母')

        if password != password2:
            return HttpResponseBadRequest('输入密码不一致')

        redis_conn = get_redis_connection('default')
        redis_sms_code = redis_conn.get('sms:%s'%mobile)
        if redis_sms_code is None:
            return HttpResponseBadRequest('短信验证码已过期')
        if smscode != redis_sms_code.decode():
            return HttpResponseBadRequest('短信验证码不一致')

        try:
            user=User.objects.create_user(username=mobile,mobile=mobile,password=password)
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest('注册失败')


        from django.contrib.auth import login
        login(request,user)

        #暂时返回成功消息，后期再跳转指定页面
        response = redirect(reverse('home:index'))
        #return HttpResponse('注册成功，重定向到首页')
        response.set_cookie('is_login',True)
        response.set_cookie('username',user.username,max_age=7*24*3600)

        return response

from django.http.response import HttpResponseBadRequest
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse
import redis
class ImageCodeView(View):

    def get(self,request):

        uuid = request.GET.get('uuid')

        if uuid is None:
            return HttpResponseBadRequest('没有传递uuid')

        text,image = captcha.generate_captcha()

        redis_conn = get_redis_connection('default')
        redis_conn.setex('img:%s'%uuid,300,text)

        return HttpResponse(image,content_type='image/jpeg')


from django.http.response import JsonResponse
from utils.response_code import RETCODE
from random import randint
from libs.yuntongxun.sms import CCP

class SmsCodeView(View):

    def get(self,request):

        mobile=request.GET.get('mobile')
        image_code=request.GET.get('image_code')
        uuid=request.GET.get('uuid')

        if not all([mobile,image_code,uuid]):
            return JsonResponse({'code':RETCODE.NECESSARYPARAMERR,'errmsg':'缺少必要的参数'})

        redis_conn=get_redis_connection('default')
        redis_image_code=redis_conn.get('img:%s'%uuid)

        if redis_image_code is None:
            return JsonResponse({'code':RETCODE.IMAGECODEERR,'errmsg':'图片验证码已过期'})

        try:
            redis_conn.delete('img:%s'%uuid)
        except Exception as e:
            logger.error(e)

        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code':RETCODE.IMAGECODEERR,'errmsg':'图片验证码错误'})

        sms_code='%06d'%randint(0,999999)
        logger.info(sms_code)
        redis_conn.setex('sms:%s'%mobile,300,sms_code)

        CCP().send_template_sms(mobile,[sms_code,5],1)

        return JsonResponse({'code':RETCODE.OK,'errmsg':'短信发送成功'})



class LoginView(View):

    def get(self,request):

        return render(request,'login.html')

    def post(self,request):

        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return HttpResponseBadRequest('手机号不符合规则')

        if not re.match(r'^[a-zA-Z0-9]{8,20}$',password):
            return HttpResponseBadRequest('密码不符合规则')

        from django.contrib.auth import authenticate

        user = authenticate(mobile=mobile,password=password)

        if user is None:
            return HttpResponseBadRequest('用户名或密码错误')

        from django.contrib.auth import login
        login(request, user)


        response = redirect(reverse('home:index'))

        if remember != 'on':
            request.session.set_expiry(0)
            response.set_cookie('is_login',True)
            response.set_cookie('username',user.username,max_age=14*24*3600)
        else:
            request.session.set_expiry(None)
            response.set_cookie('is_login', True,max_age=14*24*3600)
            response.set_cookie('username', user.username, max_age=14 * 24 * 3600)

        return response

