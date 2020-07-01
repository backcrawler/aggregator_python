from django.contrib import admin
from .models import Site, Post, BadCodeEvent, ExceptionEvent, Pic


@admin.register(Site)
class SiteModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    pass


@admin.register(BadCodeEvent)
class BadCodeEventModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ExceptionEvent)
class ExceptionEventModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Pic)
class ExceptionEventModelAdmin(admin.ModelAdmin):
    pass
