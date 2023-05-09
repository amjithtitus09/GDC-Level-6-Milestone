# Add all your views here
from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ValidationError

from tasks.models import Task

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views import View
from django.forms import ModelForm

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin

tasks = []


class AbstractTaskQuerySet(LoginRequiredMixin):
    
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user = self.request.user).order_by("priority")
    
class UserSignupView(CreateView):
    form_class = UserCreationForm
    template_name = "user_signup.html"
    success_url= "/user/login"

class UserLoginView(LoginView):
    template_name = "user_login.html"

def session_storage_view(request):
    total_views = request.session.get("total_views", 0)
    request.session["total_views"] = total_views + 1
    return HttpResponse(f"Total Views {total_views}")

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        tasks = Task.objects.filter(deleted=False, user = self.request.user).order_by("completed", "priority")
        search_term = self.request.GET.get("search")
        if search_term:
            tasks = tasks.filter(title__icontains=search_term)
        print(tasks)
        return tasks

class TaskCreateForm(ModelForm):

    class Meta:
        model = Task
        fields = ("title", "description", "priority", "completed")

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 10:
            raise ValidationError("Title is too short")
        return title.upper()

class TaskCreateView(AbstractTaskQuerySet, CreateView):
    form_class = TaskCreateForm
    template_name = "add_task.html"
    success_url = "/tasks"

    def check_and_move_down_task(self, priority):
        task_to_modify = self.get_queryset().filter(priority=priority)
        if not task_to_modify:
            return False
        else:
            if self.check_and_move_down_task(priority+1):
                return True
            else:
                task_to_modify = task_to_modify.get()
                task_to_modify.priority = priority+1
                task_to_modify.save()


    def form_valid(self, form):
        
        self.check_and_move_down_task(form.cleaned_data["priority"])
        self.object = form.save()
        
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
    

class TaskUpdateView(AbstractTaskQuerySet, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "update_task.html"
    success_url = "/tasks"

class TaskDeleteView(AbstractTaskQuerySet, DeleteView):
    model = Task
    template_name = "delete_task.html"
    success_url = "/tasks"

class TaskCompleteView(AbstractTaskQuerySet, UpdateView):
    model = Task
    template_name = "complete_task.html"
    success_url = "/tasks"

class TaskDetailView(AbstractTaskQuerySet, DetailView):
    model = Task

class AddTaskView(View):
    def get(self, request):
        return render(request, "add_task.html")
    
    def post(self, request):
        Task(title = request.POST.get("task")).save()
        return HttpResponseRedirect("/tasks")

class CompletedTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "completed_tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        return Task.objects.filter(completed=True, deleted=False, user = self.request.user)


def complete_task_view(request, index):
    Task.objects.filter(id=index).update(completed=True)
    return HttpResponseRedirect("/tasks")