from django.db import models

import importlib
from urllib.parse import urlparse

m = importlib.import_module('news.parsers')
parsers = {}
for key, val in vars(m).items():
    if key.endswith('_parser'):
        name = key[:-7]
        parsers[name] = val


class ActiveManager(models.Manager):
    # TODO: finish this
    ...


class Post(models.Model):
    WEB = 'web_dev'
    DS = 'data_science'
    cats = (
        (WEB, 'Web Development'),
        (DS, 'Data Science'),
    )
    title = models.CharField(max_length=255)
    category = models.CharField(choices=cats, max_length=16, null=True, default=None, blank=True)
    ref = models.URLField(unique=True, db_index=True)
    source = models.ForeignKey(to='Site', on_delete=models.SET_NULL, null=True, default=None, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    #objects = models.Manager()  # TODO: decide on this

    class Meta:
        ordering = ('-created', 'ref')

    def save(self, *args, **kwargs):
        print('save method')
        if self.source is None:
            print('Source is None...')
            parsed_url = urlparse(self.ref)
            source_field = parsed_url.netloc
            print('source field:', source_field)
            try:
                source_site = Site.objects.get(ref=source_field)  # finding out if Site with this ref exists
            except Site.DoesNotExist:
                print('No source found')
                self.source = None  # nothing changed here
            else:
                print('got a source:', source_site)
                self.source = source_site  # automatically set source
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Post(ref: {self.ref}, id:{self.id})'


class Site(models.Model):
    name = models.CharField(max_length=128, unique=True)
    ref = models.CharField(max_length=128)
    active = models.BooleanField(default=True)

    # objects = models.Manager()  # TODO: decide on this

    def _handle_resource(self):
        res_name = self.name
        url = self.ref
        handler = parsers[res_name]
        return handler(url)

    def work_on_resource(self):
        results = self._handle_resource()
        for res in results:
            post = Post(source=self, **res)
            try:
                Post.objects.get(ref=post.ref)
            except Post.DoesNotExist:
                post.save()

    def __str__(self):
        return f'Site(name: {self.name}, id:{self.id})'