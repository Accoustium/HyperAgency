"""hyperjob URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import MainMenuView, MySignUpView, UserHomePage
import sys
sys.path.append('..')
from resume.views import MainResumeView, AddResumeView
from vacancy.views import MainVacancyView, AddVacancyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', LoginView.as_view(template_name="hyperjob/login.html"), name="login"),
    path('', MainMenuView.as_view(), name="index"),
    path('resumes/', MainResumeView.as_view(), name="resume_index"),
    path('resume/new', AddResumeView.as_view(), name="new_resume"),
    path('signup', MySignUpView.as_view(), name="signup"),
    path('vacancies/', MainVacancyView.as_view(), name="vacancy_index"),
    path('vacancy/new', AddVacancyView.as_view(), name="new_vacancy"),
    path('home/', UserHomePage.as_view(), name="home"),
    path('logout/', LogoutView.as_view(), name="logout")
]
