import django
from django.views import View
from django.shortcuts import render, redirect
from .models import Vacancy
from .forms import vacancyForm
from django.core.exceptions import PermissionDenied


# Create your views here.
class MainVacancyView(View):
    template_name = "vacancy/vacancy.html"

    def get(self, request, *agrs, **kwargs):
        vacancies = Vacancy.objects.all()

        return render(request, self.template_name, context={'vacancies': vacancies})


class AddVacancyView(View):
    template_name = "vacancy/new_vacancy.html"
    form_class = vacancyForm()

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return render(request, self.template_name, context={'form': self.form_class})

        raise PermissionDenied

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff:
                self.form_class = vacancyForm(request.POST)
                if self.form_class.is_valid():
                    Vacancy.objects.create(author=request.user, description=self.form_class.cleaned_data['description'])
                    return redirect("vacancy_index")

        raise PermissionDenied
