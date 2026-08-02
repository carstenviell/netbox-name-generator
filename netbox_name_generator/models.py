from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import IntegrityError, models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

kuerzel_validator = RegexValidator(
    r'^[A-Z0-9]+$',
    _('Only uppercase letters (A–Z) and digits (0–9) allowed.'),
)

# Defense in depth for HIGH-01 (stored XSS): "beschreibung" values flow into a
# JSON structure embedded on the name-generator page. The template now uses
# |json_script (HTML-escapes safely regardless of content), but this blocks
# HTML metacharacters at the source too, since a free-text description field
# has no legitimate need for them.
beschreibung_validator = RegexValidator(
    r'^[^<>]*$',
    _('The characters < and > are not allowed.'),
)

ZAEHLUNG_NG_CHOICES = [
    ('ohne_rack', _('Without Rack Suffix (number unique per location/type/function)')),
    ('vollstaendig', _('Full Name (number unique per rack — same number may appear in different racks)')),
    ('standort_uebergreifend', _('Cross-location (number globally unique per type/function)')),
]

ZAEHLUNG_STD_CHOICES = [
    ('praefix', _('Location-local (number unique per location/purpose)')),
    ('standort_uebergreifend', _('Cross-location (number globally unique per purpose)')),
]


class Standort(NetBoxModel):
    kuerzel = models.CharField(
        max_length=6,
        unique=True,
        validators=[kuerzel_validator],
        verbose_name=_('Abbreviation'),
    )
    beschreibung = models.CharField(
        max_length=100, blank=True, validators=[beschreibung_validator], verbose_name=_('Description'),
    )
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
    beschreibung = models.CharField(
        max_length=100, blank=True, validators=[beschreibung_validator], verbose_name=_('Description'),
    )
    hat_funktion = models.BooleanField(
        default=True,
        verbose_name=_('Has Function'),
        help_text=_('Disable for types without function abbreviation (e.g. AP)'),
    )
    zaehlung_strategie = models.CharField(
        max_length=30,
        choices=ZAEHLUNG_NG_CHOICES,
        default='ohne_rack',
        verbose_name=_('Counting Strategy'),
        help_text=_('Determines how duplicate numbers are detected when generating names.'),
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
    beschreibung = models.CharField(
        max_length=100, blank=True, validators=[beschreibung_validator], verbose_name=_('Description'),
    )

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
    beschreibung = models.CharField(
        max_length=100, blank=True, validators=[beschreibung_validator], verbose_name=_('Description'),
    )

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
    beschreibung = models.CharField(
        max_length=100, blank=True, validators=[beschreibung_validator], verbose_name=_('Description'),
    )

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
    beschreibung = models.CharField(
        max_length=100, blank=True, validators=[beschreibung_validator], verbose_name=_('Description'),
    )

    class Meta:
        ordering = ['kuerzel']
        verbose_name = _('VM Function')
        verbose_name_plural = _('VM Functions')

    def __str__(self):
        return self.kuerzel

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('plugins:netbox_name_generator:vmfunktion_edit', kwargs={'pk': self.pk})


class NamierungsKonfiguration(NetBoxModel):
    max_laenge = models.PositiveSmallIntegerField(
        default=15,
        validators=[MinValueValidator(10), MaxValueValidator(63)],
        verbose_name=_('Max. Name Length'),
        help_text=_('Maximum number of characters for generated names (default: 15).'),
    )
    nummer_stellen = models.PositiveSmallIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Counter Digits'),
        help_text=_('Number of digits for the auto-counter (default: 2 → 01–99).'),
    )
    strategie_netzwerkgeraet = models.CharField(
        max_length=30,
        choices=ZAEHLUNG_NG_CHOICES,
        default='ohne_rack',
        verbose_name=_('Network Device Counting Strategy'),
    )
    strategie_server = models.CharField(
        max_length=30,
        choices=ZAEHLUNG_STD_CHOICES,
        default='praefix',
        verbose_name=_('Server Counting Strategy'),
    )
    strategie_pc = models.CharField(
        max_length=30,
        choices=ZAEHLUNG_STD_CHOICES,
        default='praefix',
        verbose_name=_('PC Counting Strategy'),
    )

    class Meta:
        verbose_name = _('Naming Configuration')
        verbose_name_plural = _('Naming Configuration')

    def __str__(self):
        return f'Naming Configuration (max. {self.max_laenge} chars, {self.nummer_stellen}-digit counter)'

    def clean(self):
        super().clean()
        if NamierungsKonfiguration.objects.exclude(pk=self.pk).exists():
            raise ValidationError(_('Only one naming configuration is allowed. Edit the existing one.'))

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('plugins:netbox_name_generator:konfiguration')


# MEDIUM-02 mitigation: the plugin never creates a Device/VirtualMachine
# itself - it only redirects to NetBox's own creation page with a prefilled
# ?name=..., so the actual object may not be saved until the user finishes
# that separate form (possibly minutes later). Without this, two concurrent
# generations for the same site/type/function could both read the same
# "next free number" snapshot and suggest the identical name. A short-lived
# reservation row, inserted atomically (unique constraint) at generation
# time and counted alongside real Device/VirtualMachine names, closes that
# window without the plugin having to create a full placeholder object with
# a guessed site/role/device_type. Reservations are cheap to let expire -
# an abandoned generation just frees the name back up after RESERVATION_TTL.
class ReservedName(models.Model):
    name = models.CharField(max_length=63, unique=True)
    reserved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


RESERVATION_TTL = timedelta(minutes=10)


def active_reserved_names():
    """Active (non-expired) reservations, to be unioned into the caller's
    existing-names collision set. Opportunistically deletes expired rows so
    the table doesn't grow unbounded - an abandoned generation (user never
    finished the NetBox add-device/VM form) just frees the name back up,
    no separate cleanup job needed."""
    ReservedName.objects.filter(reserved_at__lt=timezone.now() - RESERVATION_TTL).delete()
    return set(ReservedName.objects.values_list('name', flat=True))


def reserve_name(name):
    """Atomically reserve `name` via the unique constraint. Returns True if
    reserved, False if another request reserved the exact same name in the
    (small) window between the caller's own existing-names snapshot and
    this call - the residual race active_reserved_names() alone can't close."""
    try:
        with transaction.atomic():
            ReservedName.objects.create(name=name)
        return True
    except IntegrityError:
        return False
