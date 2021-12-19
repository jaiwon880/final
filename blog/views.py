from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Post,Comment
from .forms import PostForm, PostModelForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView

#함수형 뷰의 매개변수로는 request로 받음
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date').order_by('-created_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        # Form 데이터를 입력하고 등록요청 시 보여주는 부분
        form = PostForm(request.POST)
        # Form 데이터가 clean 한 상태
        if form.is_valid():
            # PostForm 으로 저장하는 법
            print(form.cleaned_data)
            post = Post.objects.create(author=User.objects.get(username=request.user),
                                       published_date=timezone.now(),
                                       title=form.cleaned_data['title'],
                                       text=form.cleaned_data['text'])
            # Post ModelForm 으로 저장하는 법
            # title, text 필드의 값이 저장된다.
            # post = form.save(commit=False)
            # post.author = User.objects.get(username=request.user)
            # post.published_date = timezone.now()
            # DB에 등록됨
            # post.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        # 등록 Form 보여주는 부분
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostModelForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = User.objects.get(username=request.user)
            post.published_date = timezone.now()
            post.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostModelForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('blog:post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('blog:post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('blog:post_detail', pk=post_pk)
