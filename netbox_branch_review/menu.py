from netbox.plugins import PluginMenu, PluginMenuItem

menu = PluginMenu(
    label="Branch Review",
    groups=(
        (
            "Change Management",
            (
                PluginMenuItem(
                    link="plugins:netbox_branch_review:changerequest_list",
                    link_text="Change Requests",
                ),
                PluginMenuItem(
                    link="plugins:netbox_branch_review:changerequest_add",
                    link_text="Add Change Request",
                ),
            ),
        ),
    ),
)
