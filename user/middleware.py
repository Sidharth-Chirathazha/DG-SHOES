from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from importlib import import_module
from django.urls import reverse

# class SeparateSessionEngineMiddleware(SessionMiddleware):
#     def process_request(self, request):
#         admin_url = reverse('admin:index')
#         if request.path.startswith(admin_url):
#             engine = import_module(settings.ADMIN_SESSION_ENGINE)
#             request.session = engine.SessionStore()
#             request.session_cookie_name = settings.ADMIN_SESSION_COOKIE_NAME
#         else:
#             super().process_request(request)

#     def process_response(self, request, response):
#         admin_url = reverse('admin:index')
#         if request.path.startswith(admin_url):
#             response.set_cookie(settings.ADMIN_SESSION_COOKIE_NAME, request.session.session_key)
#         else:
#             super().process_response(request, response)

#         return response