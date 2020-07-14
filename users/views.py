from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls.base import reverse
from django.contrib.auth import login, authenticate

from .forms import UserCreationForm


def register(request):
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            # redirect...
            authenticated_user = authenticate(username=new_user.username,
                                              password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('news:mainpage'))
    context = {'form': form}
    return render(request, 'users/register.html', context)


# for u in User.objects.all():
#     try:
#         u.profile
#     except User.profile.RelatedObjectDoesNotExist:
#         Profile.objects.create(user=u)
