from django import forms

from .models import Post, Site
from .utils import compose_name

CATS = Post.cats
SITES = tuple((site.name, compose_name(site.name)) for site in Site.objects.all())


class PrefCatForm(forms.Form):
    categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CATS, required=False)
    sites = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=SITES, required=False)
