from django.test import TestCase
from django.shortcuts import reverse


class MainpageTests(TestCase):
    fixtures = ['post_fixture.json']

    def test_mainpage_load(self):
        url = reverse('news:mainpage')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def send_cookies(self, data):
        endpoint = reverse('news:userpost')
        response = self.client.post(endpoint, data)
        return response

    def test_posting(self):
        d1 = {'user_categories': ['wev_dev']}
        response = self.send_cookies(d1)
        self.assertEqual(response.status_code, 302)
        #auth
        #send again