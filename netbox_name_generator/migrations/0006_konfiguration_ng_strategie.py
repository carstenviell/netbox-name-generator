from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_name_generator', '0005_ng_strategie_standort'),
    ]

    operations = [
        migrations.AddField(
            model_name='namierungskonfiguration',
            name='strategie_netzwerkgeraet',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('ohne_rack', 'Without Rack Suffix (number unique per location/type/function)'),
                    ('vollstaendig', 'Full Name (number unique per rack — same number may appear in different racks)'),
                    ('standort_uebergreifend', 'Cross-location (number globally unique per type/function)'),
                ],
                default='ohne_rack',
                verbose_name='Network Device Counting Strategy',
            ),
        ),
    ]
