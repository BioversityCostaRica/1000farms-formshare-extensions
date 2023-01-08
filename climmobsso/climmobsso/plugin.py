import formshare.plugins as plugins
import formshare.plugins.utilities as u
from .views import ClimMobLogin, ClimMobLoginSuccess, ClimMobLoginPage
import sys
import os


class ClimMobSSO(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.IConfig)
    plugins.implements(plugins.ITranslation)

    def before_mapping(self, config):
        # We don't add any routes before the host application
        return []

    def after_mapping(self, config):
        # We add here a new route /json that returns a JSON
        custom_map = [
            u.add_route(
                "climmob_sso_login", "/climmobsoo/sso_login", ClimMobLogin, None
            ),
            u.add_route(
                "climmob_sso_success",
                "/climmobsoo/sso_success",
                ClimMobLoginSuccess,
                None,
            ),
            u.add_route("login", "/login", ClimMobLoginPage, "generic/login.jinja2"),
        ]
        return custom_map

    def update_config(self, config):
        # We add here the templates of the plugin to the config
        u.add_templates_directory(config, "templates")

    def get_translation_directory(self):
        module = sys.modules["climmobsso"]
        return os.path.join(os.path.dirname(module.__file__), "locale")

    def get_translation_domain(self):
        return "climmobsso"
