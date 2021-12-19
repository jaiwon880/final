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

from guardian.conf import settings as guardian_settings
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm, get_objects_for_user

from .models import Survey, Question, Choice, SurveyAssignment, SurveyResponse

import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from polls.forms import RenewBookForm



class SurveyManagerView(UserPassesTestMixin, View):

    def test_func(self):
        self.obj = Survey.objects.get(pk=self.kwargs['survey_id'])
        return self.obj.created_by.id == self.request.user.id

    def get(self, request, survey_id):

        users = User.objects.exclude(Q(pk=request.user.id) | Q(username=guardian_settings.ANONYMOUS_USER_NAME))
        assigned_users = {
            sa.assigned_to.id
            for sa in SurveyAssignment.objects.filter(survey=self.obj)
        }

        context = {
            'survey': self.obj,
            'available_assignees': [u for u in users if u.id not in assigned_users],
            'available_reviewers': [u for u in users if not u.has_perm('can_view_results', self.obj)]
        }
        return render(request, 'survey/manage_survey.html', context)

    def post(self, request, survey_id):
        assignees = request.POST.getlist('assignees')
        reviewers = request.POST.getlist('reviewers')

        perm = Permission.objects.get(codename='view_surveyassignment')
        for assignee_id in assignees:
            assigned_to = User.objects.get(pk=int(assignee_id))
            assigned_survey = SurveyAssignment.objects.create(
                survey=self.obj,
                assigned_by=request.user,
                assigned_to=assigned_to
            )
            assign_perm(perm, assigned_to, assigned_survey)

        group = Group.objects.get(name=f"survey_{self.obj.id}_result_viewers")
        for reviewer_id in reviewers:
            reviewer = User.objects.get(pk=int(reviewer_id))
            reviewer.groups.add(group)
            reviewer.save()

        return redirect(reverse('profile'))


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


class SurveyResultsView(PermissionRequiredMixin, View):
    permission_required = 'survey.can_view_results'

    def get_object(self):
        self.obj = get_object_or_404(Survey, pk=self.kwargs['survey_id'])
        return self.obj

    def get(self, request, survey_id):
        questions = []
        for question in self.obj.questions.all():
            question_vm = QuestionViewModel(question.text)
            for choice in question.choices.all():
                question_vm.choices.append(ChoiceResultViewModel(choice.id, choice.text))

            for survey_response in SurveyResponse.objects.filter(question=question):
                question_vm.add_survey_response(survey_response)

            questions.append(question_vm)

        context = {'survey': self.obj, 'questions': questions}

        return render(request, 'survey/survey_result.html', context)



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


class SurveyCreateView(LoginRequiredMixin, View):
    def get(self, request):
        users = User.objects.all()
        return render(request, 'survey/create_survey.html', {'users': users})

    def post(self, request):
        data = request.POST

        title = data.get('title')
        questions_json = data.getlist('questions')
        assignees = data.getlist('assignees')
        reviewers = data.getlist('reviewers')
        valid = True
        context = {}
        if not title:
            valid = False
            context['title_error'] = 'title is required'

        if not questions_json:
            valid = False
            context['questions_error'] = 'questions are required'

        if not assignees:
            valid = False
            context['assignees_error'] = 'assignees are required'

        if not valid:
            context['users'] = User.objects.all()
            return render(request, 'survey/create_survey.html', context)

        survey = Survey.objects.create(title=title, created_by=request.user)
        for question_json in questions_json:
            question_data = json.loads(question_json)
            question = Question.objects.create(text=question_data['text'], survey=survey)
            for choice_data in question_data['choices']:
                Choice.objects.create(text=choice_data['text'], question=question)
        perm = Permission.objects.get(codename='view_surveyassignment')
        for assignee in assignees:
            assigned_to = User.objects.get(pk=int(assignee))
            assigned_survey = SurveyAssignment.objects.create(
                survey=survey,
                assigned_by=request.user,
                assigned_to=assigned_to
            )
            assign_perm(perm, assigned_to, assigned_survey)

        group = Group.objects.create(name=f"survey_{survey.id}_result_viewers")
        assign_perm('can_view_results', group, survey)
        request.user.groups.add(group)
        request.user.save()

        for reviewer_id in reviewers:
            reviewer = User.objects.get(pk=int(reviewer_id))
            reviewer.groups.add(group)
            reviewer.save()

        return redirect(reverse('profile'))

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



class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        surveys = Survey.objects.filter(created_by=request.user).all()
        assigned_surveys = SurveyAssignment.objects.filter(assigned_to=request.user).all()
        survey_results = get_objects_for_user(request.user, 'can_view_results', klass=Survey)

        context = {
          'surveys': surveys,
          'assgined_surveys': assigned_surveys,
          'survey_results': survey_results
        }

        return render(request, 'survey/profile.html', context)

class RegisterView(View):
    def get(self, request):
        return render(request, 'polls/register.html', { 'form': UserCreationForm() })

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse('login'))

        return render(request, 'polls/register.html', { 'form': form })