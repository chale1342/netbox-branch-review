from extras.plugins import PluginMenuItem, PluginMenuButton

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_branch_review:changerequest_list",
        link_text="Change Requests",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_branch_review:changerequest_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color="green",
            ),
        ),
    ),
)