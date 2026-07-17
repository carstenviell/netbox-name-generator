from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_name_generator', '0003_namierungskonfiguration'),
    ]

    operations = [
        migrations.AddField(
            model_name='netzwerkgeraettyp',
            name='zaehlung_strategie',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('ohne_rack', 'Without Rack Suffix (number unique per location/type/function)'),
                    ('vollstaendig', 'Full Name (number unique per rack — same number may appear in different racks)'),
                ],
                default='ohne_rack',
                verbose_name='Counting Strategy',
            ),
        ),
        migrations.AddField(
            model_name='namierungskonfiguration',
            name='strategie_server',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('praefix', 'Location-local (number unique per location/purpose)'),
                    ('standort_uebergreifend', 'Cross-location (number globally unique per purpose)'),
                ],
                default='praefix',
                verbose_name='Server Counting Strategy',
            ),
        ),
        migrations.AddField(
            model_name='namierungskonfiguration',
            name='strategie_pc',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('praefix', 'Location-local (number unique per location/purpose)'),
                    ('standort_uebergreifend', 'Cross-location (number globally unique per purpose)'),
                ],
                default='praefix',
                verbose_name='PC Counting Strategy',
            ),
        ),
    ]
