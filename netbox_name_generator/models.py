from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

kuerzel_validator = RegexValidator(
    r'^[A-Z0-9]+$',
    _('Only uppercase letters (A–Z) and digits (0–9) allowed.'),
)


class Standort(NetBoxModel):
    kuerzel = models.CharField(
        max_length=6,
        unique=True,
        validators=[kuerzel_validator],
        verbose_name=_('Abbreviation'),
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name=_('Description'))
    site = models.ForeignKey(
        'dcim.Site',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='name_generator_standorte',
        verbose_name=_('NetBox Site'),
        help_text=_('Link to NetBox site – pre-filled when creating a device.'),
    )

    class Meta:
        ordering = ['kuerzel']
        verbose_name = _('Site')
        verbose_name_plural = _('Sites')

    def __str__(self):
        if self.site_id:
            return f'{self.kuerzel} – {self.site.name}'
        return self.kuerzel

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('plugins:netbox_name_generator:standort_edit', kwargs={'pk': self.pk})


class NetzwerkgeraetTyp(NetBoxModel):
    kuerzel = models.CharField(
        max_length=4,
        unique=True,
        validators=[kuerzel_validator],
        verbose_name=_('Abbreviation'),
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name=_('Description'))
    hat_funktion = models.BooleanField(
        default=True,
        verbose_name=_('Has Function'),
        help_text=_('Disable for types without function abbreviation (e.g. AP)'),
    )

    class Meta:
        ordering = ['kuerzel']
        verbose_name = _('Network Device Type')
        verbose_name_plural = _('Network Device Types')

    def __str__(self):
        return self.kuerzel

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('plugins:netbox_name_generator:netzwerkgeraettyp_edit', kwargs={'pk': self.pk})


class NetzwerkgeraetFunktion(NetBoxModel):
    typ = models.ForeignKey(
        NetzwerkgeraetTyp,
        on_delete=models.CASCADE,
        related_name='funktionen',
        verbose_name=_('Type'),
    )
    kuerzel = models.CharField(
        max_length=4,
        validators=[kuerzel_validator],
        verbose_name=_('Abbreviation'),
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name=_('Description'))

    class Meta:
        ordering = ['typ__kuerzel', 'kuerzel']
        unique_together = [('typ', 'kuerzel')]
        verbose_name = _('Network Device Function')
        verbose_name_plural = _('Network Device Functions')

    def __str__(self):
        return f'{self.typ.kuerzel} – {self.kuerzel}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('plugins:netbox_name_generator:netzwerkgeraetfunktion_edit', kwargs={'pk': self.pk})


class ServerZweck(NetBoxModel):
    kuerzel = models.CharField(
        max_length=4,
        unique=True,
        validators=[kuerzel_validator],
        verbose_name=_('Abbreviation'),
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name=_('Description'))

    class Meta:
        ordering = ['kuerzel']
        verbose_name = _('Server Purpose')
        verbose_name_plural = _('Server Purposes')

    def __str__(self):
        return self.kuerzel

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('plugins:netbox_name_generator:serverzweck_edit', kwargs={'pk': self.pk})


class VmBereich(NetBoxModel):
    kuerzel = models.CharField(
        max_length=4,
        unique=True,
        validators=[kuerzel_validator],
        verbose_name=_('Abbreviation'),
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name=_('Description'))

    class Meta:
        ordering = ['kuerzel']
        verbose_name = _('VM Area')
        verbose_name_plural = _('VM Areas')

    def __str__(self):
        return self.kuerzel

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('plugins:netbox_name_generator:vmbereich_edit', kwargs={'pk': self.pk})


class VmFunktion(NetBoxModel):
    kuerzel = models.CharField(
        max_length=3,
        unique=True,
        validators=[kuerzel_validator],
        verbose_name=_('Abbreviation'),
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name=_('Description'))

    class Meta:
        ordering = ['kuerzel']
        verbose_name = _('VM Function')
        verbose_name_plural = _('VM Functions')

    def __str__(self):
        return self.kuerzel

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('plugins:netbox_name_generator:vmfunktion_edit', kwargs={'pk': self.pk})
