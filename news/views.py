from django.shortcuts import Http404, HttpResponseRedirect, reverse
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Post
from .forms import PrefCatForm, CATS, SITES
from .utils import listify


class PostListView(ListView):
    '''shows all posts, category (cat) specifies the post type'''
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
                categories = cookies.get('user_categories')
                sites = cookies.get('user_sites')
                if not (categories or sites):  # logged in, but no cookie yet
                    queryset = Post.objects.all()
                else:  # if required cookies are set
                    queryset = Post.objects.all()
                    if categories:
                        query = Q(category=None)
                        for val, _ in CATS:
                            if val in cookies['user_categories']:
                                query.add(Q(category=val), Q.OR)
                        queryset = queryset.filter(query)
                    if sites:
                        query = Q()
                        for val, _ in SITES:
                            if val in cookies['user_sites']:
                                query.add(Q(source__name=val), Q.OR)
                        queryset = queryset.filter(query)
            else:  # AnonymousUser, showing all results
                queryset = Post.objects.all()  # TODO: exclude reddit
        return queryset.order_by('-created')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if context.get('is_paginated'):
            page_obj = context.get('page_obj')
            if page_obj.has_previous():
                context['prev_url'] = '?page={}'.format(page_obj.previous_page_number())
            else:
                context['prev_url'] = ''
            if page_obj.has_next():
                context['next_url'] = '?page={}'.format(page_obj.next_page_number())
            else:
                context['next_url'] = ''
        categories_string = self.request.COOKIES.get('user_categories', '')
        sites_string = self.request.COOKIES.get('user_sites', '')
        if categories_string or sites_string:
            context['form'] = PrefCatForm(data={'categories': listify(categories_string),
                                                'sites': listify(sites_string)})
        else:  # if these cookies have not been set yet
            context['form'] = PrefCatForm()  # TODO: correct data set
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
