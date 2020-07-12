from django import forms

from .models import Post, Site
from .utils import compose_name

PERIODS = ( ('all_time', 'All time'), ('3days', '3 days'), ('7days', '7 days'), ('1month', 'Last month') )
CATS = Post.cats
SITES = tuple((site.name, compose_name(site.name)) for site in Site.objects.all())


class PrefCatForm(forms.Form):
    period = forms.ChoiceField(widget=forms.Select(), choices=PERIODS, required=False, label='Period')
    categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CATS, required=False)
    sites = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=SITES, required=False)
