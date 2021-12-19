from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, reverse
from django.views import View

from .forms import QuestionForm
from .models import Question, Choice
from django.template import loader
from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from django.http import Http404
from django.views import generic
from django.utils import timezone

import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, reverse, get_object_or_404

from django.views import View

from .models import Survey, Question, Choice, SurveyAssignment, SurveyResponse

import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from polls.forms import RenewBookForm


class QuestionViewModel:
    def __init__(self, text, choices=[]):
        self.text = text
        self.choices = choices

    def add_survey_response(self, survey_response):
        for choice in self.choices:
            if choice.id == survey_response.choice.id:
                choice.responses += 1
                break


class ChoiceResultViewModel:
    def __init__(self, id, text, responses=0):
        self.id = id
        self.text = text
        self.responses = responses


def question_list(request):
    questions = Question.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'polls/index.html', {'questions': questions})

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render(request, 'polls/detail.html', {'question': question})

def question_new(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.published_date = timezone.now()
            question.save()
            return redirect('polls:detail', pk=question.pk)
        #GET request.method가 오면
    else:
        form = QuestionForm()
        return render(request, 'polls/full_result.html', {'form': form})

# Create your views here.
class IndexView(generic.ListView): #()인자안에 부모 클래스가 들어감
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    """Return the last five published questions."""
    def get_queryset(self):
        return Question.objects.order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

class FullResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/full_result.html'


def vote(request,question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        return render(request,'polls/detail.html',{
            'questions':question,
            'error_message':"You didn't select a choice",
        })
    else:
        selected_choice.votes +=1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


class PollFeed(generic.DetailView):
    title = "Polls"
    link = "/polls"
    description = "Latest Polls"

    def items(self):
        return Question.objects.all().order_by('-pub_date')

    def item_link(self, poll):
        return reverse('polls:detail', args=(poll.id,))

    def item_pubdate(self, poll):
        return poll.pub_date


class RegisterView(View):
    def get(self, request):
        return render(request, 'polls/register.html', { 'form': UserCreationForm() })

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse('login'))

        return render(request, 'polls/register.html', { 'form': form })