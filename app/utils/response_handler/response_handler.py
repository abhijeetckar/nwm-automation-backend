import copy

from starlette.responses import JSONResponse

from app.utils.error_handling.standard_error_message import standard_errors
from app.utils.error_handling.standard_http_code import standard_http_code
from fastapi.encoders import jsonable_encoder

from app.models.common_model import StandarErrorResponseModel


class APIResponse:

    def __init__(self,request_id:str,status_code:str,data:dict={},errors:dict={}):
        self.request_id = request_id
        self.status_code = status_code
        self.data = data
        self.errors = errors


    async def error_generators(self):
        error_list = []
        for error_type,args in self.errors.items():
            errors = standard_errors.get(error_type,None)
            if errors is not None and len(args) == 0:
                error_list.append(jsonable_encoder(StandarErrorResponseModel(**errors)))
            elif errors is not None:
                for arg in args:
                    temp_errors = copy.deepcopy(errors)
                    for  sub_arg in arg.split('-'):
                        temp_errors["error_message"] = temp_errors["error_message"].replace("%s",sub_arg,1)
                        temp_errors["error_display_msg"] = temp_errors["error_display_msg"].replace("%s", sub_arg, 1)
                    error_list.append(jsonable_encoder(StandarErrorResponseModel(**temp_errors)))
        return error_list


    async def response_model(self,errors=[]):
        obj = {
            "reqId":self.request_id,
            "errors":list(errors) if len(errors) !=0 else self.errors,
            "data":self.data
        }
        return JSONResponse(status_code=standard_http_code.get(self.status_code),content=obj)

