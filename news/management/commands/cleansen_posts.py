from django.core.management.base import BaseCommand, CommandError
from news.models import Post


class Command(BaseCommand):
    help = 'Clears duplicates by title'

    def add_arguments(self, parser):
        parser.add_argument('src_name', type=str)

    def handle(self, *args, **kwargs):
        from random import shuffle
        src_name = kwargs.get('src_name')
        cur_posts = Post.objects.filter(source__name=src_name)
        shuffle(cur_posts)
        title_set = set()
        bad_posts = []
        for post in cur_posts:
            if post.title in title_set:
                bad_posts.append(post)
            title_set.add(post.title)
        for p in bad_posts:
            p.delete()
        WHOLE_LEN = len(bad_posts)
        if WHOLE_LEN:
            print(f'INFO: {WHOLE_LEN} posts were removed succesfully')
        else:
            print('INFO: Nothing to remove here. All unique')