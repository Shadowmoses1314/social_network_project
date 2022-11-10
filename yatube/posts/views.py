from core.utils import paginate_page
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    page_obj = paginate_page(request, post_list)
    return render(request, 'posts/index.html', {'page_obj': page_obj, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginate_page(request, posts)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page_obj,
        },
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = paginate_page(request, post_list)
    following = author.following.filter(author=author)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginate_page(request, posts)
    context = {
        'page_obj': page_obj,
        'posts': posts,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if not request.user.follower.filter(
            user=request.user,
            author=user).exists() and request.user != user:
        Follow.objects.create(user=request.user, author=user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    author = Follow.objects.filter(
        user=request.user, author=author).delete()
    return redirect('posts:profile', username)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    author = request.user
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'author': author,
            'form': form,
            'comments': comments
        },
    )


@login_required
def add_comment(request, post_id):
    # Получите пост
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    context = {'form': form}
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id != post.author.id:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        post.save()
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)
