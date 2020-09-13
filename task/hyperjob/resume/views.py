import django
from django.views import View
from django.shortcuts import render, redirect
from .models import Resume
from .forms import resumeForm
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied


# Create your views here.
class MainResumeView(View):
    template_name = "resume\\resumes.html"

    def get(self, request, *agrs, **kwargs):
        resumes = Resume.objects.all()

        return render(request, self.template_name, context={'resumes': resumes})


class AddResumeView(View):
    template_name = "resume/new_resume.html"
    form_class = resumeForm()

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, self.template_name, context={'form': self.form_class})

        raise PermissionDenied

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.form_class = resumeForm(request.POST)
            if self.form_class.is_valid():
                Resume.objects.create(author=request.user, description=self.form_class.cleaned_data['description'])
                return redirect("resume_index")

        raise PermissionDenied
