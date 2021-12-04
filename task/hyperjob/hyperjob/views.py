from django.views import View
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy


# Create your views here.
class MainMenuView(View):
    template_name = "hyperjob/main_menu.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class MySignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "hyperjob/signup.html"


class UserHomePage(View):
    template_name = "hyperjob/home.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
