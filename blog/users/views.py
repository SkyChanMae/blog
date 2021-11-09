from django.shortcuts import render

# Create your views here.
from django.views import View


class RegisterView(View):

    def get(self,request):

        return render(request,'register.html')


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