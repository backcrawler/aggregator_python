import datetime
import pytz
from django.test import TestCase

from news.models import BadCodeEvent, ExceptionEvent, Site, Post

utc = pytz.UTC


class EventsTest(TestCase):
    def test_exception(self):
        event = ExceptionEvent.objects.create(exc_text='Cant reach server', resource=None)
        self.assertEqual(ExceptionEvent.objects.count(), 1)
        self.assertEqual(event.exc_text, 'Cant reach server')
        self.assertNotEqual(event.date_occured, None)

    def test_resp_code(self):
        event = BadCodeEvent.objects.create(resp_code=404, resource=None)
        self.assertEqual(BadCodeEvent.objects.count(), 1)
        self.assertEqual(event.resp_code, 404)


class CoreModelsTest(TestCase):
    def setUp(self):
        self.s = Site.objects.create(name='Test Site', ref='www.google.com/resource3232')

    def test_site_object(self):
        self.assertEqual(Site.objects.count(), 1)
        self.assertEqual(self.s.active, True)
        self.assertEqual(self.s.ref, 'www.google.com/resource3232')

    def test_post_object(self):
        packed = {'title': 'Random Post here', 'ref': 'www.google.com/randomidnumber'}
        post = Post.objects.create(source=self.s, **packed)
        self.assertEqual(Post.objects.count(), 1)
        self.assertGreaterEqual(utc.localize(datetime.datetime.today()), post.created)
        self.assertEqual(post.source, self.s)
        self.assertEqual(post.category, None)


class DataLoadTest(TestCase):
    fixtures = ['top_sites_fixture.json']

    def setUp(self):
        self.sites = Site.objects.all()

    def test_minor_case(self):
        self.assertEqual(len(self.sites), 9)  # the number of fixtures provided

    def test_data_fetching(self):
        for site in self.sites:
            results = site._handle_resource()
            self.assertNotEqual(len(results), 0)

    # def test_data_writing(self):
    #     for site in self.sites:
    #         site.work_on_resource()
    #     self.assertEqual(ExceptionEvent.objects.count(), 0)
    #     self.assertEqual(BadCodeEvent.objects.count(), 0)
