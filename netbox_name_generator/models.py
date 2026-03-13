from django.core.validators import RegexValidator
from django.db import models
from netbox.models import NetBoxModel

kuerzel_validator = RegexValidator(
    r'^[A-Z0-9]+$',
    'Nur Großbuchstaben (A–Z) und Ziffern (0–9) erlaubt.',
)


class Standort(NetBoxModel):
    kuerzel = models.CharField(
        max_length=6,
        unique=True,
        validators=[kuerzel_validator],
        verbose_name='Kürzel',
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name='Beschreibung')
    site = models.ForeignKey(
        'dcim.Site',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='name_generator_standorte',
        verbose_name='NetBox-Site',
        help_text='Verknüpfung mit dem NetBox-Standort – wird beim Gerät-Anlegen vorausgefüllt.',
    )

    class Meta:
        ordering = ['kuerzel']
        verbose_name = 'Standort'
        verbose_name_plural = 'Standorte'

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
        verbose_name='Kürzel',
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name='Beschreibung')
    hat_funktion = models.BooleanField(
        default=True,
        verbose_name='Hat Funktion',
        help_text='Deaktivieren für Typen ohne Funktionskürzel (z. B. AP)',
    )

    class Meta:
        ordering = ['kuerzel']
        verbose_name = 'Netzwerkgerät-Typ'
        verbose_name_plural = 'Netzwerkgerät-Typen'

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
        verbose_name='Typ',
    )
    kuerzel = models.CharField(
        max_length=4,
        validators=[kuerzel_validator],
        verbose_name='Kürzel',
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name='Beschreibung')

    class Meta:
        ordering = ['typ__kuerzel', 'kuerzel']
        unique_together = [('typ', 'kuerzel')]
        verbose_name = 'Netzwerkgerät-Funktion'
        verbose_name_plural = 'Netzwerkgerät-Funktionen'

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
        verbose_name='Kürzel',
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name='Beschreibung')

    class Meta:
        ordering = ['kuerzel']
        verbose_name = 'Server-Zweck'
        verbose_name_plural = 'Server-Zwecke'

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
        verbose_name='Kürzel',
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name='Beschreibung')

    class Meta:
        ordering = ['kuerzel']
        verbose_name = 'VM-Bereich'
        verbose_name_plural = 'VM-Bereiche'

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
        verbose_name='Kürzel',
    )
    beschreibung = models.CharField(max_length=100, blank=True, verbose_name='Beschreibung')

    class Meta:
        ordering = ['kuerzel']
        verbose_name = 'VM-Funktion'
        verbose_name_plural = 'VM-Funktionen'

    def __str__(self):
        return self.kuerzel

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('plugins:netbox_name_generator:vmfunktion_edit', kwargs={'pk': self.pk})
