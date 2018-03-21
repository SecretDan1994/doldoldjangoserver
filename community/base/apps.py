from django.apps import AppConfig

class BaseConfig(AppConfig):
    name = 'base'

    def ready(self):
        from .util import site_setting_ensure
        site_setting_ensure.on_ready()