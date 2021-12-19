import datetime

from django import forms
from django.db import models
from django.forms import formset_factory
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now()-datetime.timedelta(days=1)

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean =True
    was_published_recently.short_description = 'Published recently?'

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text



class Survey(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='surveys'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SurveyAssignment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(
        Survey,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='survey_assignments'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_surveys_to'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_surveys'
    )


class SurveyResponse(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    survey_assigned = models.ForeignKey(
        SurveyAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='question_responses'
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='choices_selected'
    )


