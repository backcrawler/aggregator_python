from celery.schedules import crontab
from celery import shared_task
from celery.task import periodic_task
from celery.utils.log import get_task_logger
from django.core.mail import mail_admins

import pytz
import datetime
from datetime import timedelta

from .concurrent_executors import DjangoConnectionThreadPoolExecutor
from aggregator_python.celeryapp import app

logger = get_task_logger(__name__)

POST_LIFE = 120
EVENT_LIFE = 14
utc = pytz.UTC


@periodic_task(run_every=timedelta(minutes=5), name='data_scrap')
def data_scrap():
    """
    Procedure for data scrapping, uses interface provided by Site class from news.models
    """
    from .models import Site
    sites = Site.objects.all()
    # for site in sites:
    #     site.work_on_resource()
    with DjangoConnectionThreadPoolExecutor(max_workers=sites.count()) as executor:
        executor.map(lambda s: s.work_on_resource(), sites)


@periodic_task(run_every=timedelta(days=1), name='db_clean')
def clean_outdated():
    """
    Cleans outdated posts and events objects
    """
    # old posts
    from .models import Post, BadCodeEvent, ExceptionEvent
    unwanted_posts = Post.objects.filter(
        date_occured__lt=utc.localize(datetime.datetime.today() - timedelta(days=POST_LIFE)))
    logger.info('POSTS DELETED: ', unwanted_posts)
    unwanted_posts.delete()
    # old code errors
    unwanted_code_events = BadCodeEvent.objects.filter(
        date_occured__lt=utc.localize(datetime.datetime.today() - timedelta(days=EVENT_LIFE)))
    unwanted_code_events.delete()
    # old exception errors
    unwanted_exception_events = ExceptionEvent.objects.filter(
        date_occured__lt=utc.localize(datetime.datetime.today() - timedelta(days=EVENT_LIFE)))
    unwanted_exception_events()


@app.task(bind=True)
def email_task(self, **kwargs):
    '''Send notification info about errors to admins'''
    subject = "Aggregator: Error occured"
    err_txt = kwargs.get('exc_text')
    invalid_code = kwargs.get('resp_code')
    if err_txt:
        start = f"Exception ({err_txt})"
    elif invalid_code:
        start = f"Bad response code ({invalid_code})"
    else:
        start = f"Unknown instance"
    message = f"{start} occured on {kwargs.get('resource')}"
    # Sending:
    logger.info('Sending email...')
    mail_admins(subject=subject,
                message=message,
                fail_silently=False)
