from django.shortcuts import render, HttpResponse, redirect
from .forms import BlogForm
from .models import Blog
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    return redirect('blog:create')

@login_required
def publish_blog(request, slug=None):
    if request.method == 'POST':
        if slug == None:
            form = BlogForm(request.POST)
            if form.is_valid():
                messages.success(request, 'Blog successfully published')
                form.instance.user = request.user
                form.instance.published = True
                form.instance.published_date = timezone.now()
                obj = form.save()
                slug = obj.slug
                return redirect('blog:details', args=(slug, ))
        else:
            try:
                blog = Blog.objects.get(slug=slug, user=request.user)
            except Blog.DoesNotExist:
                return render(request, 'blog/form.html', {'error': True})
            form = BlogForm(request.POST, instance=blog)
            if form.is_valid():
                messages.success(request, 'Blog successfully published')
                if blog.published == False:
                    form.instance.published = True
                    form.instance.published_date = timezone.now()
                obj = form.save()
                slug = obj.slug
                return redirect('blog:details', args=(slug, ))
    else:
        if slug == None:
            form = BlogForm()
        else:
            try:
                blog = Blog.objects.get(slug=slug, user=request.user)
            except Blog.DoesNotExist:
                return render(request, 'blog/form.html', {'error': True})
            form = BlogForm(instance=blog)
        published = blog.published
        return render(request, 'blog/form.html', {'form': form, 'published': published})

@login_required
def create(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            blog = form.save()
            if request.POST.get('publish'):
                return render(request, 'blog/confirm_publish.html', {'blog': blog})
            else:
                return render(request, 'blog/details.html', {'blog': blog})
    else:
        form = BlogForm()
    return render(request, 'blog/form.html', {'form': form})

@login_required
def update(request, slug):
    try:
        blog = Blog.objects.get(slug=slug, user=request.user)
    except Blog.DoesNotExist:
        return render(request, 'blog/form.html', {'error': True})
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            blog = form.save()
            if request.POST.get('publish'):
                return render(request, 'blog/confirm_publish.html', {'blog': blog})
            else:
                return render(request, 'blog/details.html', {'blog': blog})
    else:
        form = BlogForm(instance=blog)
    return render(request, 'blog/update_form.html', {'form': form})

@login_required
def confirm_publish(request, slug):
    try:
        blog = Blog.objects.get(slug=slug, user=request.user)
    except Blog.DoesNotExist:
        return render(request, 'blog/details.html', {'error': True})
    if blog.published == False:
        blog.published = True
        blog.published_date = timezone.now()
    blog.save()
    return render(request, 'blog/details.html', {'blog': blog})

def blog_details(request, slug):
    try:
        if request.user.is_authenticated:
            blog = Blog.objects.get(slug=slug, user=request.user)
            return render(request, 'blog/details.html', {'blog': blog})
        else:
            raise Blog.DoesNotExist
    except Blog.DoesNotExist:
        try:
            blog = Blog.objects.get(slug=slug, published=True)
            return render(request, 'blog/details.html', {'blog': blog})
        except Blog.DoesNotExist:
            return render(request, 'blog/details.html', {'error': True})

@login_required
def blog_list(request):
    blogs = Blog.objects.filter(user=request.user).order_by('-created_date')
    return render(request, 'blog/list.html', {'blogs': blogs, 'type': 1})

@login_required
def blog_draft_list(request):
    blogs = Blog.objects.filter(user=request.user, published=False).order_by('-created_date')
    return render(request, 'blog/list.html', {'blogs': blogs, 'type': 3})

@login_required
def blog_published_list(request):
    blogs = Blog.objects.filter(user=request.user, published=True).order_by('-published_date')
    return render(request, 'blog/list.html', {'blogs': blogs, 'type': 2})
