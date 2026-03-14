from django.utils.translation import gettext_lazy as _

from netbox.plugins.navigation import ButtonColorChoices, PluginMenuButton, PluginMenuItem

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_name_generator:index',
        link_text='Name Generator',
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:standort_list',
        link_text=_('Sites'),
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:standort_add',
                title=_('Add Site'),
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:netzwerkgeraettyp_list',
        link_text=_('ND Types'),
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:netzwerkgeraettyp_add',
                title=_('Add ND Type'),
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:netzwerkgeraetfunktion_list',
        link_text=_('ND Functions'),
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:netzwerkgeraetfunktion_add',
                title=_('Add ND Function'),
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:serverzweck_list',
        link_text=_('Server Purposes'),
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:serverzweck_add',
                title=_('Add Server Purpose'),
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:vmbereich_list',
        link_text=_('VM Areas'),
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:vmbereich_add',
                title=_('Add VM Area'),
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:vmfunktion_list',
        link_text=_('VM Functions'),
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:vmfunktion_add',
                title=_('Add VM Function'),
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
)
