from django.shortcuts import Http404, HttpResponseRedirect, reverse, render
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Post
from .forms import PrefCatForm, CATS, SITES
from .utils import listify


class PostListView(ListView):
    '''Shows all posts, category (cat) specifies the post type'''
    template_name = "news/home.html"
    model = Post
    http_method_names = ('get', 'head', 'options')
    allow_empty = True
    paginate_by = 15
    cat = None

    def get_queryset(self):
        if self.cat is not None:  # if self.cat is provided, showing all result for it
            queryset = Post.objects.filter(category=self.cat)
        else:
            if self.request.user.is_authenticated:  # user is logged in
                cookies = self.request.COOKIES
                categories = cookies.get('user_categories', '')
                sites = cookies.get('user_sites', '')
                queryset = Post.objects.all()
                query = Q(category=None)
                for val, _ in CATS:
                    if val in categories:
                        query.add(Q(category=val), Q.OR)
                queryset = queryset.filter(query)
                query = Q(source__name=None)
                for val, _ in SITES:
                    if val in sites:
                        query.add(Q(source__name=val), Q.OR)
                queryset = queryset.filter(query)
            else:  # AnonymousUser, showing all results
                queryset = Post.objects.all()
        return queryset.order_by('-created')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        categories_string = self.request.COOKIES.get('user_categories', '')
        sites_string = self.request.COOKIES.get('user_sites', '')
        if categories_string or sites_string:
            context['form'] = PrefCatForm(data={'categories': listify(categories_string),
                                                'sites': listify(sites_string)})
        else:  # if these cookies have not been set yet
            context['form'] = PrefCatForm(data={'categories': list(map(lambda c: c[0], CATS)),
                                                'sites': list(map(lambda s: s[0], SITES))})
        return context


@login_required
def userform_submitting(request):
    '''For POST-requests from the front, sets required cookies'''
    if request.method != 'POST':
        return Http404
    response = HttpResponseRedirect(redirect_to=reverse('news:mainpage'))
    categories = request.POST.getlist('categories')
    sites = request.POST.getlist('sites')
    response.set_cookie('user_categories', categories, max_age=2592000)
    response.set_cookie('user_sites', sites, max_age=2592000)
    return response


def err(request, errcode):
    '''For testing custom error pages'''
    if errcode == '500':
        return render(request, '500.html')
    elif errcode == '404':
        return render(request, '404.html')
    else:
        return HttpResponseRedirect(redirect_to=reverse('news:mainpage'))


# @login_required
# def ajax_userform_submitting(request):
#     print('COOKIES_RECEIVED:', request.COOKIES)
#     if request.method != 'POST':
#         return Http404
#     response = HttpResponse()
#     print('POST:', request.POST)
#     categories = request.POST.getlist('categories')
#     print('CATEGORIES:', categories)
#     # pol = ('pol', True if 'Politics' in categories else False)
#     # eco = ('eco', True if 'Economy' in categories else False)
#     # sport = ('sport', True if 'Sports' in categories else False)
#     # values_to_set = [pol, eco, sport]
#     # print('values_to_set:', values_to_set)
#     response.set_cookie('user_categories', categories, max_age=2592000)
#     print('COOKIES_MODIFIED:', request.COOKIES)
#     return HttpResponse(json.dumps({}), content_type="application/json")
