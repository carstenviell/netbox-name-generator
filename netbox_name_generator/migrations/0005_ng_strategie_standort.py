from django.db import migrations, models


class Migration(migrations.Migration):
    """State-only migration: adds 'standort_uebergreifend' choice to NetzwerkgeraetTyp.zaehlung_strategie."""

    dependencies = [
        ('netbox_name_generator', '0004_zaehlung_strategien'),
    ]

    operations = [
        migrations.AlterField(
            model_name='netzwerkgeraettyp',
            name='zaehlung_strategie',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('ohne_rack', 'Without Rack Suffix (number unique per location/type/function)'),
                    ('vollstaendig', 'Full Name (number unique per rack — same number may appear in different racks)'),
                    ('standort_uebergreifend', 'Cross-location (number globally unique per type/function)'),
                ],
                default='ohne_rack',
                verbose_name='Counting Strategy',
            ),
        ),
    ]
