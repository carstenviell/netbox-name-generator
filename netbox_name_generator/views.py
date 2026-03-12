from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import NameGeneratorForm

TEMPLATE = 'netbox_name_generator/name_generator.html'


class NameGeneratorView(LoginRequiredMixin, View):
    """
    GET:  Formular anzeigen
    POST: Formular validieren → bei Erfolg Redirect zu NetBox-Erstellungsseite
          mit vorausgefülltem ?name=...-Parameter
    """

    def get(self, request):
        form = NameGeneratorForm()
        return render(request, TEMPLATE, {'form': form})

    def post(self, request):
        form = NameGeneratorForm(request.POST)
        if form.is_valid():
            return redirect(form.target_url)
        return render(request, TEMPLATE, {'form': form})
