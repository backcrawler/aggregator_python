from django.db import models
from django.core.mail import mail_admins, send_mail

from .utils import ResponceCodeError
from .managers import ActiveManager

import sys
import importlib
import traceback
from urllib.parse import urlparse

DEFAULT_PIC_ID = 1

m = importlib.import_module('news.parsers')
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

    def notify_admins(self):
        '''Send notification info about errors to admins'''
        subject = "Aggregator: Error occured"
        err_txt = self.__dict__.get('exc_text')
        invalid_code = self.__dict__.get('resp_code')
        if err_txt:
            start = f"Exception ({err_txt})"
        elif invalid_code:
            start = f"Bad response code ({invalid_code})"
        else:
            start = f"Unknown instance"
        message = f"{start} occured on {self.resource} at {self.date_occured}."
        # Sending:
        print('gotta send')
        mail_admins(subject=subject,
                    message=message,
                    fail_silently=False)

    def save(self, *args, **kwargs):
        today_qs = self.__class__.objects.filter(date_occured=self.date_occured, resource=self.resource)
        print(today_qs)
        if not today_qs.exists():  # if such error didn't occur for today, send info in email
            print('sending email...')
            self.notify_admins()
        super().save(*args, **kwargs)


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

    def __str__(self):
        return f'Post(ref: {self.ref}, id:{self.id})'


class Site(models.Model):
    '''Represent a "root"-resource where initial data is leached from; handles data fetching in methods'''
    name = models.CharField(max_length=128, unique=True)
    ref = models.CharField(max_length=128)
    img = models.ForeignKey(to='Pic', on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)

    objects = ActiveManager()
    old_manager = models.Manager()

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


class Pic(models.Model):
    '''Represents logo picture for a site/post instance'''
    tag = models.CharField(max_length=32)
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return f'Pic({self.tag})'