# Create your views here.
from ads.models import Ad,Comment,Fav
from ads.owner import OwnerListView, OwnerDetailView, OwnerDeleteView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from ads.forms import CreateForm,CommentForm
from django.urls import reverse
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import naturaltime

class AdListView(OwnerListView):
    model = Ad
    # By convention:
    template_name = "ads/ad_list.html"
    #  template_name = "favs/list.html"

    def get(self, request) :
        # the ads should be filter first befor pass to the templates
        # ad_list = Ad.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_ads.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]

        strval =  request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # __icontains for case-insensitive search
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            query.add(Q(tags__name__in=[strval]), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().distinct().order_by('-updated_at')[:10]
        else :
            ad_list = Ad.objects.all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in ad_list:
            obj.natural_updated = naturaltime(obj.updated_at)


        ctx = {'ad_list' : ad_list, 'favorites': favorites, 'search': strval}
        return render(request, self.template_name, ctx)


class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ads/ad_detail.html"
    def get(self, request, pk) :
        ad = get_object_or_404(Ad, id=pk)
        comments = Comment.objects.filter(ad=ad).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'ad' : ad, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)


# class AdCreateView(OwnerCreateView):
#     model = Ad
#     # List the fields to copy from the Article model to the Article form
#     fields = ['title', 'text','price']

# class AdUpdateView(OwnerUpdateView):
#     model = Ad
#     fields = ['title', 'text','price']
#     # This would make more sense
#     # fields_exclude = ['owner', 'created_at', 'updated_at']


class AdDeleteView(OwnerDeleteView):
    model = Ad


class AdCreateView(LoginRequiredMixin, View):
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()
        # https://django-taggit.readthedocs.io/en/latest/forms.html#commit-false
        form.save_m2m()    # Add this
        return redirect(self.success_url)


class AdUpdateView(LoginRequiredMixin, View):
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')

    def get(self, request, pk):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=ad)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=ad)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()

        # https://django-taggit.readthedocs.io/en/latest/forms.html#commit-false
        form.save_m2m()    # Add this

        return redirect(self.success_url)

def stream_file(request, pk):
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id])
# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
