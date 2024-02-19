from django.utils.deprecation import MiddlewareMixin


class CustomMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # This method is called before the view
        # You can modify the request here
        print("here in middleware", request.headers, request.user)
        return None
