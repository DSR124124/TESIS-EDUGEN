from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Course, Grade, Section

# Create your views here.

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'academic/course/management.html'
    context_object_name = 'courses'

class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    fields = ['name', 'code', 'description', 'credits', 'is_active']
    template_name = 'academic/course/form.html'
    success_url = reverse_lazy('academic:course_list')

class GradeListView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = 'academic/grade/list.html'
    context_object_name = 'grades'

class SectionListView(LoginRequiredMixin, ListView):
    model = Section
    template_name = 'academic/section/management.html'
    context_object_name = 'sections'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grades'] = Grade.objects.all()
        return context
