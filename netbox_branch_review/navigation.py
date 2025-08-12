from netbox.plugins import PluginMenu, PluginMenuItem

menu = PluginMenu(
    label='Branch Review',
    groups=(
        ('Change Management', (
            PluginMenuItem(
                link='plugins:netbox_branch_review:changerequest_list',
                link_text='Change Requests',
                auth_required=True,  # or use permissions=['netbox_branch_review.view_changerequest']
            ),
        )),
    ),
    icon_class='mdi mdi-source-branch',
)
