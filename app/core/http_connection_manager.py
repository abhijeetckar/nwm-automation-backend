import httpx


class HTTPConnectionManager:
    '''
        class: Helps to manage the http request
        http_url: Http request url
        method: This is the http request method(ex: get,post,put,patch,delete)
        request_body: Optional parameter
        headers: Optional parameter

    '''

    def __init__(self, request_id, http_url, method, request_json=None, headers={}, request_params={}, ):
        self._http_url = http_url
        self._method = method
        self._request_json = request_json
        self._headers = headers
        self._request_timeout = 23
        self._request_params = request_params
        self._request_id = request_id

    async def get_response_data(self, response):
        content_type = response.headers.get('content-type')
        if content_type is not None and 'application/json' in content_type.lower():
            return response.json()
        else:
            return response.text

    async def _no_authentication(self):
        response = None
        async with httpx.AsyncClient(timeout=self._request_timeout, verify=False) as client:
            response = await client.request(method=self._method.lower(), url=self._http_url, headers=self._headers,
                                            json=self._request_json, params=self._request_params)
        return response

    async def _token_authentication(self, auth_token, token_key):
        response = None
        async with httpx.AsyncClient(timeout=self._request_timeout) as client:
            self._headers[token_key] = auth_token
            response = await client.request(method=self._method.lower(), url=self._http_url, headers=self._headers,
                                            json=self._request_json, params=self._request_params)
        return response
