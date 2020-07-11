from django.core.management.base import BaseCommand, CommandError
from news.models import Post

from urllib.parse import urlparse, urlunparse


class Command(BaseCommand):
    help = 'Removes unnecessary url endings'

    def add_arguments(self, parser):
        parser.add_argument('src_name', type=str)

    def handle(self, *args, **kwargs):
        src_name = kwargs.get('src_name')
        cur_posts = Post.objects.filter(source__name=src_name)
        counter = 0
        for post in cur_posts:
            parsed = urlparse(post.ref)
            correct_ref = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
            if correct_ref == post.ref:
                continue
            post.ref = correct_ref
            counter += 1
            post.save()
        print(f'INFO: {counter} post urls were fixed')