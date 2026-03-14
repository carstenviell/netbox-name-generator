from netbox.plugins import PluginConfig


class NameGeneratorConfig(PluginConfig):
    name = 'netbox_name_generator'
    verbose_name = 'Name Generator'
    description = 'Automatically generates device names based on configurable parameters. Once confirmed, navigates directly to the device creation form.'
    version = '1.2.0'
    author = 'Carsten Viell'
    base_url = 'name-generator'


config = NameGeneratorConfig
