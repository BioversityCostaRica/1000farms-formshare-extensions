import formshare.plugins as plugins
import formshare.plugins.utilities as u
import sys
import os


class Branding(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfig)
    plugins.implements(plugins.ITranslation)

    def update_config(self, config):
        # We add here the templates of the plugin to the config
        u.add_templates_directory(config, "templates")
        u.add_static_view(config, "1000FARMS", "static")

    def get_translation_directory(self):
        module = sys.modules["branding"]
        return os.path.join(os.path.dirname(module.__file__), "locale")

    def get_translation_domain(self):
        return "branding"
