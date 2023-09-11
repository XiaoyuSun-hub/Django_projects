from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from cats.models import Cat,Breed
from django.urls import reverse_lazy
# Create your views here.
# Take the easy way out on the main table
# These views do not need a form because CreateView, etc.
# Build a form object dynamically based on the fields
# value in the constructor attributes
class MainView(LoginRequiredMixin, View):
    def get(self, request):
        mc = Breed.objects.count()
        al = Cat.objects.all()

        ctx = {'breed_count': mc, 'cat_list': al}
        return render(request, 'cats/cat_list.html', ctx)


class BreedView(LoginRequiredMixin, View):
    def get(self, request):
        ml = Breed.objects.all()
        ctx = {'breed_list': ml}
        return render(request, 'cats/breed_list.html', ctx)


class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    fields = '__all__'
    success_url = reverse_lazy('cats:all')


class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    fields = '__all__'
    success_url = reverse_lazy('cats:all')


class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    fields = '__all__'
    success_url = reverse_lazy('cats:all')

    # We use reverse_lazy() because we are in "contructor attribute" code
# that is run before urls.py is completely loaded
class BreedCreate(LoginRequiredMixin, CreateView):
    model = Breed
    fields = '__all__'
    success_url = reverse_lazy('cats:all')
    # return redirect(self.success_url)

# and no form by extending UpdateView
class BreedUpdate(LoginRequiredMixin, UpdateView):
    model = Breed
    fields = '__all__'
    success_url = reverse_lazy('cats:all')


class BreedDelete(LoginRequiredMixin, DeleteView):
    model = Breed
    fields = '__all__'
    success_url = reverse_lazy('cats:all')
