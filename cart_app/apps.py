from django.apps import AppConfig


class CartAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart_app'

    def ready(self):
         
         import cart_app.signals