from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Bookmark
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView


class BookmarkUpdateView(UpdateView):
    model = Bookmark
    fields = ['site_name', 'url']
    template_name_suffix='_update'

class BookmarkDetailView(DetailView):
    model = Bookmark

class BookmarkListView(ListView):
    model = Bookmark
    paginate_by = 6

class BookmarkCreateView(CreateView):
    model = Bookmark
    fields = ['site_name', 'url']
    success_url = reverse_lazy('bookmark:list')
    # 기본 접미사는 _form
    template_name_suffix = '_create'

class BookmarkDeleteView(DeleteView):
    model = Bookmark
    success_url = reverse_lazy('bookmark:list')