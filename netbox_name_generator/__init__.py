from netbox.plugins import PluginConfig


class NameGeneratorConfig(PluginConfig):
    name = 'netbox_name_generator'
    verbose_name = 'Name Generator'
    description = 'Generiert konforme IT-Systemnamen gemäß Unternehmensrichtlinie'
    version = '1.0.0'
    author = 'Carsten Viell'
    base_url = 'name-generator'


config = NameGeneratorConfig
