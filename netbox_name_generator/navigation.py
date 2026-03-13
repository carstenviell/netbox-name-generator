from netbox.plugins.navigation import ButtonColorChoices, PluginMenuButton, PluginMenuItem

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_name_generator:index',
        link_text='Name Generator',
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:standort_list',
        link_text='Standorte',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:standort_add',
                title='Standort hinzufügen',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:netzwerkgeraettyp_list',
        link_text='NG-Typen',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:netzwerkgeraettyp_add',
                title='NG-Typ hinzufügen',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:netzwerkgeraetfunktion_list',
        link_text='NG-Funktionen',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:netzwerkgeraetfunktion_add',
                title='NG-Funktion hinzufügen',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:serverzweck_list',
        link_text='Server-Zwecke',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:serverzweck_add',
                title='Server-Zweck hinzufügen',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:vmbereich_list',
        link_text='VM-Bereiche',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:vmbereich_add',
                title='VM-Bereich hinzufügen',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_name_generator:vmfunktion_list',
        link_text='VM-Funktionen',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_name_generator:vmfunktion_add',
                title='VM-Funktion hinzufügen',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
)
