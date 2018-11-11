from django.http import HttpResponse
from django.views import generic
from oddjobsapp.models import User, Post
from oddjobsapp.forms import SignUpForm, PostForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.views.generic import DetailView
from stream_django.enrich import Enrich
from stream_django.feed_manager import feed_manager

enricher = Enrich()



class UserView(DetailView):
    model = User
    template_name = 'templates/posts/user.html'

    def get_object(self):
        return self.get_queryset().get(username=self.kwargs['username'])

    def get_context_data(self, object):
        user = self.object
        feeds = feed_manager.get_user_feed(user.id)
        activities = feeds.get()['results']
        activities = enricher.enrich_activities(activities)

        return {
            'activities': activities,
            'user': user,
            'login_user': self.request.user
        }

class PostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'templates/posts/post.html'
    success_url = 'templates/posts/user.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(Post, self).form_valid(form)

class Index(LoginRequiredMixin, generic.ListView):
  login_url = '/login'
  redirect_field_name = ''
  template_name = 'home/index.html'
  context_object_name = 'posts_list'

  def get_queryset(user_id):
      return feed_manager.get_user_feed(user_id)

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def post(request):
    return HttpResponse("This is a dummy view")
