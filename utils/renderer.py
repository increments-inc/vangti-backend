import contextlib
from rest_framework.renderers import JSONRenderer
from rest_framework.utils import json
from rest_framework.views import exception_handler


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        message = errors = links = count = total_pages = None
        if data is not None:
            message = (
                data.pop("detail")
                if "detail" in data
                else (data.pop("message") if "message" in data else "")
            )
            errors = data.pop("errors") if "errors" in data else None
            # status = data.pop('status') if 'status' in data else (data.pop('success') if 'success' in data else 'success')
            data = data.pop("data") if "data" in data else data

            # for pagination class separate data
            links = data.pop("links") if "links" in data else {}
            count = data.pop("count") if "count" in data else 0
            total_pages = data.pop("total_pages") if "total_pages" in data else 0
            data = data.pop("results") if "results" in data else data

        stats_code = renderer_context["response"].status_code
        status = "success" if 199 < stats_code < 299 else "failure"

        response_data = {
            "message": errors[0].split(":")[1].strip() if errors else message,
            "errors": errors,
            "status": status,
            "status_code": stats_code,
            "links": links,
            "count": count,
            "total_pages": total_pages,
            "data": data or [],
        }

        with contextlib.suppress(Exception):
            getattr(
                renderer_context.get("view").get_serializer().Meta,
                "resource_name",
                "objects",
            )

        return super(CustomJSONRenderer, self).render(
            response_data, accepted_media_type, renderer_context
        )


# # custom_exception_handler.py
def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None:
        if message := response.data.get("detail"):
            response.data = {
                "data": [],
                "message": message,
                "error": [message],
                "success": "failure",
            }

        else:
            errors = [
                f'{field} : {" ".join(value)}' for field, value in response.data.items()
            ]

            response.data = {
                "data": [],
                "message": "Validation Error",
                "errors": errors,
                "status": "failure",
            }
    return response