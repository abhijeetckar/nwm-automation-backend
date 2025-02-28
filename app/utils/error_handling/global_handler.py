from app.utils.response_handler.response_handler import APIResponse


class GlobalHandler:
    def __init__(self, request):
        self.request = request

    async def global_request_validation(self, exception):
        payload_data = exception.errors()
        errors_dict = {}

        for error_data in payload_data:
            error_type = error_data.get('type', None)
            if error_type not in errors_dict:
                errors_dict[error_type] = []

        api_response_obj = APIResponse(request_id=self.request.headers.get("requestId"), status_code="client_error",
                                       errors=errors_dict)
        return await api_response_obj.response_model(errors=await api_response_obj.error_generators())
