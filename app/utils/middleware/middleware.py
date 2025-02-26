import uuid
import json

from app.utils.error_handling.loggers import  async_critical, async_info
from app.utils.error_handling.standard_http_code import standard_http_code
from app.utils.response_handler.response_handler import APIResponse
from logging import DEBUG
import inspect

class Middleware:
    def __init__(self, request):
        self.request = request

    async def execute_middleware(self, call_next):
        request_id = getattr(self.request, 'headers', {}).get("requestId", str(uuid.uuid4()))
        await async_info(request_id, inspect.currentframe().f_code.co_name, f"{request_id}")
        try:
            new_headers = getattr(self.request, 'headers', {}).mutablecopy()
            new_headers.append(
                "requestId", request_id
            )
            self.request._headers = new_headers
            self.request.scope.update(headers=getattr(self.request,'headers',{}).raw)
            api_response = await call_next(self.request)
            binary = b''
            async for data in api_response.body_iterator:
                binary += data
            api_response_json = json.loads(binary.decode())
            api_response_obj = APIResponse(request_id=getattr(self.request, 'headers', {}).get("requestId"),
                                           status_code=list(standard_http_code.keys())[
                                               list(standard_http_code.values()).index(api_response.status_code)],
                                           data=api_response_json.get("data",{}),
                                           errors=api_response_json.get("errors",[]))
            return await api_response_obj.response_model()
        except Exception as exp:
            await async_critical("",inspect.currentframe().f_code.co_name,f"{exp}")
            api_response_obj = APIResponse(request_id=request_id,
                                           status_code="client_error",
                                           errors={"error.badrequest":[str(exp)]})
            return await api_response_obj.response_model()

