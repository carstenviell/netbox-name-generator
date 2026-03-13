"""
Daten-Migration: Füllt die Parametertabellen mit den bisherigen Standardwerten.
"""

from django.db import migrations


def create_initial_data(apps, schema_editor):
    Standort = apps.get_model('netbox_name_generator', 'Standort')
    NetzwerkgeraetTyp = apps.get_model('netbox_name_generator', 'NetzwerkgeraetTyp')
    NetzwerkgeraetFunktion = apps.get_model('netbox_name_generator', 'NetzwerkgeraetFunktion')
    ServerZweck = apps.get_model('netbox_name_generator', 'ServerZweck')
    VmBereich = apps.get_model('netbox_name_generator', 'VmBereich')
    VmFunktion = apps.get_model('netbox_name_generator', 'VmFunktion')

    # Standorte
    standorte = [
        ('RZ1', 'Rechenzentrum 1'),
        ('HAU', 'Hauptgebäude'),
        ('NEB', 'Nebengebäude'),
        ('B01', 'Gebäude 01'),
    ]
    for kuerzel, beschreibung in standorte:
        Standort.objects.get_or_create(kuerzel=kuerzel, defaults={'beschreibung': beschreibung})

    # Netzwerkgerät-Typen
    typen = [
        ('SW',  'Switch',         True),
        ('FW',  'Firewall',       True),
        ('STO', 'Storage',        True),
        ('AP',  'WLAN-Accesspoint', False),
    ]
    typ_objects = {}
    for kuerzel, beschreibung, hat_funktion in typen:
        obj, _ = NetzwerkgeraetTyp.objects.get_or_create(
            kuerzel=kuerzel,
            defaults={'beschreibung': beschreibung, 'hat_funktion': hat_funktion},
        )
        typ_objects[kuerzel] = obj

    # Netzwerkgerät-Funktionen
    funktionen = {
        'SW':  [
            ('COR', 'Core'),
            ('DIS', 'Distribution'),
            ('ACC', 'Access'),
            ('EDG', 'Edge'),
        ],
        'FW':  [
            ('EXT', 'External / Perimeter'),
            ('INT', 'Internal'),
        ],
        'STO': [
            ('SAN', 'Storage Area Network'),
            ('NAS', 'Network Attached Storage'),
        ],
    }
    for typ_kuerzel, funktion_list in funktionen.items():
        typ_obj = typ_objects[typ_kuerzel]
        for kuerzel, beschreibung in funktion_list:
            NetzwerkgeraetFunktion.objects.get_or_create(
                typ=typ_obj,
                kuerzel=kuerzel,
                defaults={'beschreibung': beschreibung},
            )

    # Server-Zwecke
    server_zwecke = [
        ('ADDS', 'Active Directory Domain Services'),
        ('SQLP', 'SQL Server'),
        ('FILE', 'Dateiserver'),
        ('MONI', 'Monitoring'),
        ('SAP',  'SAP-System'),
        ('EXCH', 'Exchange'),
        ('HYPV', 'Hypervisor'),
    ]
    for kuerzel, beschreibung in server_zwecke:
        ServerZweck.objects.get_or_create(kuerzel=kuerzel, defaults={'beschreibung': beschreibung})

    # VM-Bereiche
    vm_bereiche = [
        ('APP',  'Anwendungen'),
        ('WEB',  'Webserver'),
        ('DB',   'Datenbank'),
        ('ADM',  'Administration'),
        ('RDS',  'Remote Desktop Services'),
        ('DEV',  'Entwicklung'),
        ('TEST', 'Test'),
        ('PROD', 'Produktion'),
    ]
    for kuerzel, beschreibung in vm_bereiche:
        VmBereich.objects.get_or_create(kuerzel=kuerzel, defaults={'beschreibung': beschreibung})

    # VM-Funktionen
    vm_funktionen = [
        ('BMS', 'Building Management System'),
        ('RDH', 'Remote Desktop Host'),
        ('NOC', 'Network Operations Center'),
        ('SQL', 'SQL-Server'),
        ('CRM', 'Customer Relationship Management'),
        ('ERP', 'Enterprise Resource Planning'),
        ('AD',  'Active Directory'),
        ('FIL', 'Dateiserver'),
    ]
    for kuerzel, beschreibung in vm_funktionen:
        VmFunktion.objects.get_or_create(kuerzel=kuerzel, defaults={'beschreibung': beschreibung})


def remove_initial_data(apps, schema_editor):
    # Beim Rückgängigmachen: alle Standarddatensätze löschen
    for model_name in ('VmFunktion', 'VmBereich', 'ServerZweck',
                       'NetzwerkgeraetFunktion', 'NetzwerkgeraetTyp', 'Standort'):
        model = apps.get_model('netbox_name_generator', model_name)
        model.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_name_generator', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, remove_initial_data),
    ]
