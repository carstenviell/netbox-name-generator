from django.utils.translation import gettext_lazy as _
from netbox.plugins import PluginTemplateExtension


class DeviceListButton(PluginTemplateExtension):
    models = ['dcim.device']

    def list_buttons(self):
        return (
            f'<a href="/plugins/name-generator/?from=device" class="btn btn-success">'
            f'<i class="mdi mdi-tag-plus-outline"></i> {_("Generate Name & Add")}'
            f'</a>'
        )


class VirtualMachineListButton(PluginTemplateExtension):
    models = ['virtualization.virtualmachine']

    def list_buttons(self):
        return (
            f'<a href="/plugins/name-generator/?from=vm" class="btn btn-success">'
            f'<i class="mdi mdi-tag-plus-outline"></i> {_("Generate Name & Add")}'
            f'</a>'
        )


template_extensions = [DeviceListButton, VirtualMachineListButton]
