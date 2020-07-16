from django.shortcuts import Http404, HttpResponseRedirect, reverse, render
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Post
from .forms import PrefCatForm, CATS, SITES, PERIODS
from .utils import listify
from .states import AuthHandler, AnonHandler

from datetime import datetime, timedelta
from collections import defaultdict

# for switch-case in period filtering inside PostListView
_periods_usual_dict = {'all_time': lambda qs: qs,  # qs - given queryset
                       '3days': lambda qs: qs.filter(created__gte=self.today - timedelta(days=3)),  # no error here
                       '7days': lambda qs: qs.filter(created__gte=self.today - timedelta(days=7)),
                       '1month': lambda qs: qs.filter(created__gte=self.today - timedelta(days=30)),
                       }


class PostListView(ListView):
    '''Shows all posts, category (cat) specifies the post type'''
    template_name = "news/home.html"
    model = Post
    http_method_names = ('get', 'head', 'options')
    allow_empty = True
    paginate_by = 15
    cat = None
    handler = None
    periods_dict = defaultdict(lambda: lambda qs: qs, _periods_usual_dict)  # lambda returns another lambda...

    def get_queryset(self):
        if self.request.user.is_authenticated:  # if logged in, fetching data according to profile attrs
            self.handler = AuthHandler(self)
        else:  # AnonymousUser, fetching data according to cookies
            self.handler = AnonHandler(self)
        self.handler.set_prefs()
        if self.cat is not None:  # if self.cat is provided, showing all result for it
            queryset = Post.objects.filter(category=self.cat)
        else:
            queryset = Post.objects.all()
            if self.categories or self.sites:
                query = Q(category=None)
                for val, _ in CATS:
                    if val in self.categories:
                        query.add(Q(category=val), Q.OR)
                queryset = queryset.filter(query)
                query = Q(source__name=None)
                for val, _ in SITES:
                    if val in self.sites:
                        query.add(Q(source__name=val), Q.OR)
                queryset = queryset.filter(query)
            if self.period:
                self.today = datetime.today()
                queryset = self.periods_dict[self.period](queryset)
        return queryset.order_by('-created')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.categories or self.sites:
            context['form'] = PrefCatForm(data={'categories': listify(self.categories),
                                                'sites': listify(self.sites),
                                                'period': self.period})
        else:  # if these cookies have not been set yet
            context['form'] = PrefCatForm(data={'categories': list(map(lambda c: c[0], CATS)),
                                                'sites': list(map(lambda s: s[0], SITES)),
                                                'period': PERIODS[0][0]})
        return context


class UserformProcessing(RedirectView):
    url = reverse_lazy('news:mainpage')
    handler = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.request.user.is_authenticated:
            self.handler = AuthHandler(self)
        else:
            self.handler = AnonHandler(self)
        self.response = HttpResponseRedirect(redirect_to=self.get_redirect_url(*args, **kwargs))

    def get(self, request, *args, **kwargs):
        return self.response

    def post(self, request, *args, **kwargs):
        self.handler.form_process()
        return self.get(request, *args, **kwargs)


def err(request, errcode):
    '''For testing custom error pages'''
    if errcode == '500':
        return render(request, '500.html')
    elif errcode == '404':
        return render(request, '404.html')
    else:
        return HttpResponseRedirect(redirect_to=reverse('news:mainpage'))


# def userform_submitting(request):
#     '''For POST-requests from the front, sets required cookies'''
#     if request.method != 'POST':
#         return Http404
#     response = HttpResponseRedirect(redirect_to=reverse('news:mainpage'))
#     period = request.POST.get('period')
#     categories = request.POST.getlist('categories')
#     sites = request.POST.getlist('sites')
#     if request.user.is_authenticated:  # working with Profile
#         profile = request.user.profile
#         profile.attrs['user_period'] = period
#         profile.attrs['user_categories'] = categories
#         profile.attrs['user_sites'] = sites
#         profile.save()
#     else:  # working with cookies
#         response.set_cookie('user_period', period, max_age=2592000)
#         response.set_cookie('user_categories', categories, max_age=2592000)
#         response.set_cookie('user_sites', sites, max_age=2592000)
#     return response
