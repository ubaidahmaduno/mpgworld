from django.apps import AppConfig

class Mpgepmc_coreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mpgepmc_core'

    # ⭐️ Add this method to register your signals ⭐️
    def ready(self):
        import mpgepmc_core.signals