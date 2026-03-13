from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from netbox.views import generic

from .forms import NameGeneratorForm
from .model_forms import (
    NetzwerkgeraetFunktionForm,
    NetzwerkgeraetTypForm,
    ServerZweckForm,
    StandortForm,
    VmBereichForm,
    VmFunktionForm,
)
from .models import (
    NetzwerkgeraetFunktion,
    NetzwerkgeraetTyp,
    ServerZweck,
    Standort,
    VmBereich,
    VmFunktion,
)
from .tables import (
    NetzwerkgeraetFunktionTable,
    NetzwerkgeraetTypTable,
    ServerZweckTable,
    StandortTable,
    VmBereichTable,
    VmFunktionTable,
)

TEMPLATE = 'netbox_name_generator/name_generator.html'


# ---------------------------------------------------------------------------
# Name Generator (Hauptansicht)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Standort CRUD + Changelog
# ---------------------------------------------------------------------------

class StandortListView(generic.ObjectListView):
    queryset = Standort.objects.all()
    table = StandortTable

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:standort_list')


class StandortEditView(generic.ObjectEditView):
    queryset = Standort.objects.all()
    form = StandortForm

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:standort_list')


class StandortDeleteView(generic.ObjectDeleteView):
    queryset = Standort.objects.all()

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:standort_list')


class StandortChangeLogView(generic.ObjectChangeLogView):
    queryset = Standort.objects.all()


# ---------------------------------------------------------------------------
# NetzwerkgeraetTyp CRUD + Changelog
# ---------------------------------------------------------------------------

class NetzwerkgeraetTypListView(generic.ObjectListView):
    queryset = NetzwerkgeraetTyp.objects.all()
    table = NetzwerkgeraetTypTable

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:netzwerkgeraettyp_list')


class NetzwerkgeraetTypEditView(generic.ObjectEditView):
    queryset = NetzwerkgeraetTyp.objects.all()
    form = NetzwerkgeraetTypForm

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:netzwerkgeraettyp_list')


class NetzwerkgeraetTypDeleteView(generic.ObjectDeleteView):
    queryset = NetzwerkgeraetTyp.objects.all()

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:netzwerkgeraettyp_list')


class NetzwerkgeraetTypChangeLogView(generic.ObjectChangeLogView):
    queryset = NetzwerkgeraetTyp.objects.all()


# ---------------------------------------------------------------------------
# NetzwerkgeraetFunktion CRUD + Changelog
# ---------------------------------------------------------------------------

class NetzwerkgeraetFunktionListView(generic.ObjectListView):
    queryset = NetzwerkgeraetFunktion.objects.select_related('typ').all()
    table = NetzwerkgeraetFunktionTable

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:netzwerkgeraetfunktion_list')


class NetzwerkgeraetFunktionEditView(generic.ObjectEditView):
    queryset = NetzwerkgeraetFunktion.objects.all()
    form = NetzwerkgeraetFunktionForm

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:netzwerkgeraetfunktion_list')


class NetzwerkgeraetFunktionDeleteView(generic.ObjectDeleteView):
    queryset = NetzwerkgeraetFunktion.objects.all()

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:netzwerkgeraetfunktion_list')


class NetzwerkgeraetFunktionChangeLogView(generic.ObjectChangeLogView):
    queryset = NetzwerkgeraetFunktion.objects.all()


# ---------------------------------------------------------------------------
# ServerZweck CRUD + Changelog
# ---------------------------------------------------------------------------

class ServerZweckListView(generic.ObjectListView):
    queryset = ServerZweck.objects.all()
    table = ServerZweckTable

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:serverzweck_list')


class ServerZweckEditView(generic.ObjectEditView):
    queryset = ServerZweck.objects.all()
    form = ServerZweckForm

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:serverzweck_list')


class ServerZweckDeleteView(generic.ObjectDeleteView):
    queryset = ServerZweck.objects.all()

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:serverzweck_list')


class ServerZweckChangeLogView(generic.ObjectChangeLogView):
    queryset = ServerZweck.objects.all()


# ---------------------------------------------------------------------------
# VmBereich CRUD + Changelog
# ---------------------------------------------------------------------------

class VmBereichListView(generic.ObjectListView):
    queryset = VmBereich.objects.all()
    table = VmBereichTable

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:vmbereich_list')


class VmBereichEditView(generic.ObjectEditView):
    queryset = VmBereich.objects.all()
    form = VmBereichForm

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:vmbereich_list')


class VmBereichDeleteView(generic.ObjectDeleteView):
    queryset = VmBereich.objects.all()

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:vmbereich_list')


class VmBereichChangeLogView(generic.ObjectChangeLogView):
    queryset = VmBereich.objects.all()


# ---------------------------------------------------------------------------
# VmFunktion CRUD + Changelog
# ---------------------------------------------------------------------------

class VmFunktionListView(generic.ObjectListView):
    queryset = VmFunktion.objects.all()
    table = VmFunktionTable

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:vmfunktion_list')


class VmFunktionEditView(generic.ObjectEditView):
    queryset = VmFunktion.objects.all()
    form = VmFunktionForm

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:vmfunktion_list')


class VmFunktionDeleteView(generic.ObjectDeleteView):
    queryset = VmFunktion.objects.all()

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netbox_name_generator:vmfunktion_list')


class VmFunktionChangeLogView(generic.ObjectChangeLogView):
    queryset = VmFunktion.objects.all()
