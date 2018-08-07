from django.shortcuts import render, HttpResponseRedirect
from django.core.paginator import Paginator
from django.urls import reverse
from .models import NewsItem
from .forms import RegisterForm, ProfileForm
from aether.utils.misc import get_page
from django.contrib.auth.decorators import login_required


def index(request):
    news_items = NewsItem.objects.filter(deleted=False).order_by('-id')

    paginator = Paginator(news_items, 10)
    page = get_page(request)

    return render(request, 'main_site/index.html', {'news_items': paginator.get_page(page)})


def faq(request):
    return render(request, 'main_site/faq.html')


def registered(request):
    return render(request, 'main_site/registered.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('main_site:registered'))
    else:
        form = RegisterForm()

    return render(request, 'main_site/register.html', {'register_form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return HttpResponseRedirect(reverse('main_site:profile'))
    else:
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'main_site/profile.html', {
        'profile_form': profile_form,
    })
