from django.db import models


class ActiveManager(models.Manager):  # TODO: finish this
    '''Manager for Site model, picks only active instances'''
    def all(self, *args, **kwargs):
        qs_main = super().all(*args, **kwargs)
        qs = qs_main.filter(active=True)
        return qs
