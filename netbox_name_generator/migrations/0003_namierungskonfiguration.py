import django.core.validators
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_name_generator', '0002_initial_data'),
        ('extras', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NamierungsKonfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('max_laenge', models.PositiveSmallIntegerField(
                    default=15,
                    validators=[
                        django.core.validators.MinValueValidator(10),
                        django.core.validators.MaxValueValidator(63),
                    ],
                    verbose_name='Max. Name Length',
                )),
                ('nummer_stellen', models.PositiveSmallIntegerField(
                    default=2,
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(5),
                    ],
                    verbose_name='Counter Digits',
                )),
                ('tags', taggit.managers.TaggableManager(
                    help_text='A comma-separated list of tags.',
                    through='extras.TaggedItem',
                    to='extras.Tag',
                    verbose_name='Tags',
                )),
            ],
            options={
                'verbose_name': 'Naming Configuration',
                'verbose_name_plural': 'Naming Configuration',
            },
        ),
    ]
