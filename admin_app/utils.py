
# from django.contrib.auth.decorators import user_passes_test
# from django.core.exceptions import PermissionDenied

# def superuser_required(view_func):
#     @user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
#     def _wrapped_view(request, *args, **kwargs):
#         return view_func(request, *args, **kwargs)
#     return _wrapped_view