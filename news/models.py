from django.db import models

from .utils import ResponceCodeError
from .managers import ActiveManager
from .tasks import email_task

import sys
import importlib
import traceback
from urllib.parse import urlparse

m = importlib.import_module('news.parsers')  # gathering all parsers' names into one dict
parsers = {}
for key, val in vars(m).items():
    if key.endswith('_parser'):
        name = key[:-7]
        parsers[name] = val


class BadEvent(models.Model):
    '''Abstract base class for unwanted events, occured while dealing with data parsing'''
    date_occured = models.DateField(auto_now_add=True)
    resource = models.CharField(max_length=128, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        today_qs = self.__class__.objects.filter(date_occured=self.date_occured, resource=self.resource)
        print(today_qs)
        if not today_qs.exists():  # if such error didn't occur for today, send info in email
            print('sending email...')
            email_task.delay(self)
        print('saving')
        super().save(*args, **kwargs)
        print('saved!')


class ExceptionEvent(BadEvent):
    '''Event due to exception handeling'''
    exc_text = models.TextField(blank=True)

    def __str__(self):
        return f'ExceptionEvent(resource: {self.resource}, date:{self.date_occured})'


class BadCodeEvent(BadEvent):
    '''Event due to invalid response code'''
    resp_code = models.IntegerField()

    def __str__(self):
        return f'BadCodeEvent(resource: {self.resource}, date:{self.date_occured}, resp_code: {self.resp_code})'


class Post(models.Model):
    '''Represent a single post on a distance resource (ref)'''
    WEB = 'web_dev'
    DS = 'data_science'
    cats = (
        (WEB, 'Web Dev'),
        (DS, 'Data Science'),
    )
    title = models.CharField(max_length=255)
    category = models.CharField(choices=cats, max_length=16, null=True, default=None, blank=True)
    ref = models.URLField(unique=True, db_index=True)
    source = models.ForeignKey(to='Site', on_delete=models.SET_NULL, null=True, default=None, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ('-created', 'ref')

    def save(self, *args, **kwargs):
        #print('save method')
        if self.source is None:
            #print('Source is None...')
            parsed_url = urlparse(self.ref)
            source_field = parsed_url.netloc
            #print('source field:', source_field)
            try:
                source_site = Site.objects.get(ref=source_field)  # finding out if Site with this ref exists
            except Site.DoesNotExist:
                #print('No source found')
                self.source = None  # nothing changed here
            else:
                #print('got a source:', source_site)
                self.source = source_site  # automatically set source
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Post(ref: {self.ref}, id:{self.id})'


class Site(models.Model):
    '''Represent a "root"-resource where initial data is leached from; handles data fetching in methods'''
    name = models.CharField(max_length=128, unique=True)
    ref = models.CharField(max_length=128)
    active = models.BooleanField(default=True)

    # objects = models.ActiveManager()  # TODO: decide on this
    # old_manager = models.Manager()

    def _handle_resource(self):
        res_name = self.name
        url = self.ref
        handler = parsers[res_name]
        return handler(url)

    def work_on_resource(self):
        try:
            results = self._handle_resource()
        except ResponceCodeError as e:  # if requests.get returned invalid code, save the code and exit function
            BadCodeEvent.objects.create(resp_code=e.code, resource=self.ref)
            return None
        except Exception as e:  # if Exception occured, save the message and exit function
            exception_string = ''.join(traceback.format_exception(*sys.exc_info()))
            ExceptionEvent.objects.create(exc_text=exception_string, resource=self.ref)
            return None
        for res in results:
            post = Post(source=self, **res)
            try:
                Post.objects.get(ref=post.ref)
            except Post.DoesNotExist:
                post.save()

    def __str__(self):
        return f'Site(name: {self.name}, id:{self.id})'
