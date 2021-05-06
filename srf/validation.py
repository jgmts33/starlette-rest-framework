from pydantic import BaseModel


async def validate_data(*, model_class, data) -> BaseModel:
    return model_class(**data)


async def transform_errors(errors) -> dict:
    error_dict = {}
    for error in errors:
        loc = '.'.join(error['loc'])
        error_dict[loc] = error_dict.get(loc, []) + [error['msg']]
    return error_dict
