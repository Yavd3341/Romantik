import datetime
import json
import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, AnonymousUser

from django.core.files.storage import default_storage

from .models import NewsPost
from romantik.settings import MEDIA_ROOT

from .modules.compressor import ImageCompressor

# Create your views here.




def full_name(user):
    if user.last_name != '' and user.first_name != '':
        return user.first_name+' '+user.last_name
    elif user.first_name != '':
        return user.first_name
    elif user.last_name != '':
        return user.last_name
    else:
        return user.username
    

def base_context(request, **args):
    context = {}
    django_user = request.user

    context['title'] = 'none'
    context['user'] = 'none'
    context['header'] = 'none'
    context['error'] = 0
    context['is_superuser'] = False

    if len(User.objects.filter(username=django_user.username)) != 0 and type(request.user) != AnonymousUser:

        user = User.objects.get(username=django_user.username)
        context['username'] = django_user.username
        context['full_name'] = full_name(user)
        context['user'] = user

        if request.user.is_superuser:
            context['is_superuser'] = True

    if args != None:
        for arg in args:
            context[arg] = args[arg]

    return context


class HomePage(View):
    def get(self, request):
        context = base_context(request, title='Home')
        return render(request, "home.html", context)


class NewsPage(View):
    def get(self, request):

        context = base_context(request, title='Новини', header='Новини')
        context['news'] = sorted(NewsPost.objects.all(), key=lambda obj: obj.datetime)
        context['news'].reverse()
        return render(request, "news.html", context)


class AjaxPublishPost(View, LoginRequiredMixin):
    def post(self, request):
        form = request.POST

        news_post = NewsPost(
            user=request.user,
            datetime=datetime.datetime.now(),   
            content=form['news_content'],     
            img_paths="" 
        )
        news_post.save()

        result = {}
        result["result"] = "success"
        return HttpResponse(
            json.dumps(result),
            content_type="application/json"
        )


class AjaxAddPhotoToPost(View, LoginRequiredMixin):
    def post(self, request):
        form = request.POST

        # filename = 
        uploaded_file = request.FILES['upload']

        file_name = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + '_' + uploaded_file.name

        file_path = default_storage.save(file_name, uploaded_file)

        abs_file_path = os.path.join(MEDIA_ROOT, file_name)

        
        if os.stat(abs_file_path).st_size > 1024*1024:
            comressor = ImageCompressor(abs_file_path)
            comressor.compress()



        result = {}
        result["result"] = "success"
        result["filename"] = file_name
        result["url"] = "/media/"+file_path
        
        return HttpResponse(
            json.dumps(result),
            content_type="application/json"
        )


class Login(View):

    def __init__(self):
        self.error = 0

    def get(self, request):

        context = base_context(
            request, title='Вхід', header='Вхід', error=0)
        context['error'] = 0

        # context['form'] = self.form_class()
        return render(request, "signin.html", context)

    def post(self, request):
        context = {}
        form = request.POST

        username = form['username']
        password = form['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                context['name'] = username
                return HttpResponseRedirect("/")

        else:
            context = base_context(request, title='Вхід', header='Вхід')
            logout(request)
            context['error'] = 1
            # return Posts.get(self,request)
            return render(request, "signin.html", context)


class Logout(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")


class SignUp(View):
    def get(self, request):

        context = base_context(
            request, title='Реєстрація', header='Реєстрація', error=0)

        return render(request, "signup.html", context)

    def post(self, request):
        context = {}
        form = request.POST
        user_props = {}
        username = form['username']
        password = form['password']

        # new_post.author = Author.objects.get(id = request.POST.author)
        # new_post.save()
        user = User.objects.filter(username=username)
        if list(user) == []:
            for prop in form:
                if prop not in ('csrfmiddlewaretoken', 'username', 'gender', 'phone_number') and form[prop] != '':
                    user_props[prop] = form[prop]

            auth_user = User.objects.create_user(username=form['username'], **user_props)
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect("/")

        else:
            context = base_context(request, title='Реєстрація', header='Реєстрація')

            for field_name in form.keys():
                context[field_name] = form[field_name]

            context['error'] = 1
            return render(request, "signup.html", context)


class AboutUs(View):
    def get(self, request):

        context = base_context(
            request, title='Про нас', header='Про нас', error=0)

        return render(request, "about_us.html", context)

    
class Rules(View):
    def get(self, request):

        context = base_context(
            request, title='Правила клубу', header='Правила клубу', error=0)

        return render(request, "rules.html", context)


class OldRules(View):
    def get(self, request):

        context = base_context(
            request, title='Правила клубу (повні)', header='Правила клубу (повні)', error=0)

        return render(request, "old_rules.html", context)
    

class History(View):
    def get(self, request):

        context = base_context(
            request, title='Історія клубу', header='Історія клубу', error=0)

        return render(request, "history.html", context)
    

class Contacts(View):
    def get(self, request):

        context = base_context(
            request, title='Контакти', header='Контакти', error=0)

        return render(request, "contacts.html", context)


class Hymn(View):    
    def get(self, request):

        context = base_context(
            request, title='Гімн клубу', header='Гімн клубу', error=0)

        return render(request, "hymn.html", context)
    

def handler404(request, exception):
        context = base_context(
            request, title='404 - Не знайдено', header='404 - Не знайдено', error=0)
        return render(request, "old_rules.html", context)
