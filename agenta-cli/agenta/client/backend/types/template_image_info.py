# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
import datetime as dt
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class TemplateImageInfo(UniversalBaseModel):
    name: str
    size: typing.Optional[int] = None
    digest: typing.Optional[str] = None
    title: str
    description: str
    last_pushed: typing.Optional[dt.datetime] = None
    repo_name: typing.Optional[str] = None
    template_uri: typing.Optional[str] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(
            extra="allow", frozen=True
        )  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
