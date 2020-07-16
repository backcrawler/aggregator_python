from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    '''Handles requests depending on required state'''
    def __init__(self, obj):
        self.obj = obj

    @abstractmethod
    def set_prefs(self):
        '''Setting attributes according to plan'''
        pass

    def leach_data(self):
        '''Getting necesarry form data'''
        self.period = self.obj.request.POST.get('period')
        self.categories = self.obj.request.POST.getlist('categories')
        self.sites = self.obj.request.POST.getlist('sites')

    @abstractmethod
    def form_process(self):
        '''Processing the main form'''
        pass


class AuthHandler(AbstractHandler):
    '''Handler for authenticated user, based on User-Profile relation'''
    def set_prefs(self):
        profile = self.obj.request.user.profile
        self.obj.period = str(profile.attrs.get('user_period', ''))
        self.obj.categories = str(profile.attrs.get('user_categories', ''))
        self.obj.sites = str(profile.attrs.get('user_sites', ''))

    def form_process(self):
        self.leach_data()
        profile = self.obj.request.user.profile
        profile.attrs['user_period'] = self.period
        profile.attrs['user_categories'] = self.categories
        profile.attrs['user_sites'] = self.sites
        profile.save()


class AnonHandler(AbstractHandler):
    '''Handler for non-auth users, based on cookies'''
    def set_prefs(self):
        cookies = self.obj.request.COOKIES
        self.obj.period = cookies.get('user_period', '')
        self.obj.categories = cookies.get('user_categories', '')
        self.obj.sites = cookies.get('user_sites', '')

    def form_process(self):
        self.leach_data()
        self.obj.response.set_cookie('user_period', self.period, max_age=2592000)
        self.obj.response.set_cookie('user_categories', self.categories, max_age=2592000)
        self.obj.response.set_cookie('user_sites', self.sites, max_age=2592000)

