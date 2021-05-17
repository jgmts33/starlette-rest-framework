import asyncio
from typing import Union, get_type_hints

from pydantic.error_wrappers import ValidationError
from starlette.concurrency import run_in_threadpool
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import Response, JSONResponse

from srf.permissions import BasePermission
from srf.request import Request
from srf.validation import validate_data, transform_errors


class APIEndpoint(HTTPEndpoint):
    permission_classes: list[BasePermission] = []

    async def start_request(self, request) -> None:
        await self.check_permissions(request)

    async def dispatch(self) -> None:
        """
        Works like Starlette's built-in dispatch, but adds extra request
        processing and exception handling.
        """
        request = Request(self.scope, receive=self.receive)
        await self.start_request(request)

        handler_name = "get" if request.method == "HEAD" else request.method.lower()
        handler = getattr(self, handler_name, self.method_not_allowed)
        is_async = asyncio.iscoroutinefunction(handler)
        try:
            if is_async:
                response = await handler(request)
            else:
                response = await run_in_threadpool(handler, request)
        except ValidationError as e:
            response = await self.handle_validation_error(request, e)

        await response(self.scope, self.receive, self.send)

    async def handle_validation_error(self, request, error) -> JSONResponse:
        errors = error.errors()
        errors = await transform_errors(errors)
        return JSONResponse(errors, status_code=400)

    async def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    async def check_permissions(self, request) -> None:
        for permission in await self.get_permissions():
            if not permission.has_permission(request, self):
                raise HTTPException(status_code=permission.status_code, detail=permission.message)


class FormEndpoint(APIEndpoint):
    async def handle(self, method, request, raw_data) -> Response:
        data = None
        if model_class := get_type_hints(method).get('data'):
            data = await validate_data(
                model_class=model_class,
                data=raw_data,
            )

        try:
            result = await method(request, data)
        except NotImplementedError:
            return Response(status_code=405)

        if result is not None:
            if isinstance(result, Response):
                return result
            return JSONResponse(result)
        else:
            return Response(status_code=204)

    async def get(self, request) -> Response:
        return await self.handle(self.fetch, request, raw_data=request.query_params)

    async def post(self, request) -> Response:
        return await self.handle(self.submit, request, raw_data=await request.json())

    async def fetch(self, request, data) -> Union[dict,list,str,bool,Response,None]:
        raise NotImplementedError()

    async def submit(self, request, data) -> Union[dict,list,str,bool,Response,None]:
        raise NotImplementedError()

    async def options(self, request) -> Response:
        # TODO: For CORS, need to see if there's a better way to handle this
        return Response()
