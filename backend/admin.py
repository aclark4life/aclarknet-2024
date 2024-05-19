from django.contrib.admin import AdminSite


class CustomAdminSite(AdminSite):
    site_header = "Project Makefile"
    site_title = "Project Makefile"
    index_title = "Project Makefile"

    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())
        custom_model_order = {
            "newsletter": [
                "Newsletter",
                "Subscription",
                "Submission",
                "Message",
            ],
        }
        for app in app_list:
            if app["app_label"] in custom_model_order:
                app["models"].sort(
                    key=lambda x: custom_model_order[app["app_label"]].index(
                        x["object_name"]
                    )
                )
        return app_list

custom_admin_site = CustomAdminSite(name="custom_admin")
