import os

from app.core.http_connection_manager import HTTPConnectionManager


class ManufacturerOperations:
    def __init__(self):
        pass

    async def call_to_token_api(self):
        token_body = {
            "memberCode": "90296",
            "password": "P7AdrWBgtQK4j-xuvukALQ==",
            "loginId": "90296TECH"
        }
        http_instance = HTTPConnectionManager(request_id="122222322",
                                              http_url="https://www.connect2nse.com/extranet-api/login/2.0",
                                              method='post', request_json=token_body)
        response = await http_instance._no_authentication()
        response_1 = await http_instance.get_response_data(response)
        return response_1

    async def extract_the_folder(self, response):
        output_folder = os.path.join(os.getcwd(), "output")
        os.makedirs(output_folder, exist_ok=True)
        byte_data = response.content
        if byte_data[:2] == b'PK':
            file_path = os.path.join(output_folder, "output1.zip")
        elif byte_data[:2] == b'\x1f\x8b':
            file_path = os.path.join(output_folder, "output1.gz")
        else:
            file_path = os.path.join(output_folder, "output1.csv")
        with open(file_path, "wb") as file:
            file.write(byte_data)
        print(file_path)
        return file_path

    async def document_download_api(self):
        param_body = {
            "segment": "CM",
            "folderPath": "/Reports",
            "filename": "C_90296_SEC_PLEDGE_24022025_01.csv.gz"
        }
        # param_body = {
        #     "segment": "FO",
        #     "folderPath": "/Reports",
        #     "filename": "Position_NCL_FO_0_CM_90296_20250224_F_0000.csv.gz"
        # }
        http_instance = HTTPConnectionManager(request_id="122222322",
                                              http_url="https://www.connect2nse.com/extranet-api/member/file/download/2.0",
                                              method='get', request_params=param_body)
        response = await http_instance._token_authentication(
            "Bearer eyJhbGciOiJSUzI1NiJ9.eyJtZW1iZXJDZCI6IjkwMjk2Iiwic3ViIjoiOTAyOTYiLCJsb2dpbklkIjoiOTAyOTZURUNIIiwiaXNzIjoiOTAyOTZURUNIIiwiZXhwIjoxNzQwNDcyOTYwLCJpYXQiOjE3NDA0NjkzNjAsImp0aSI6IjUwZGEyOGQ5LTI3ZTQtNGJmOS1iNjUyLWQ4N2YxZTJhMjgwMyJ9.aKYzj3S3Bap8YhmxV5E85DG42BUBgkL1wTnDiHiS8BsShtQXdS5ZQZ3egibqbNSvKHpLacmCSHx1G6SUyrGNOA",
            "Authorization")
        if response.status_code == 200 and response.headers.get('content-type') is None:
            file_path = await self.extract_the_folder(response)
            return file_path
        else:
            return ""
        # return response_1

# def exchange_call():
#     # asyncio.run(ManufacturerOperations().call_to_exchange())
#     return asyncio.run(ManufacturerOperations().document_download_api())
#
# try:
#     print(exchange_call())
# except Exception as exp:
#     print(exp)
