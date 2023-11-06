from typing import Generic, List, Literal, TypeAlias, TypeVar, Union

from pydantic import BaseModel, ConstrainedInt, Field
from pydantic.generics import GenericModel


class ErrorCodeGt(ConstrainedInt):
    gt = 200


class ErrorCodeLt(ConstrainedInt):
    lt = 200


ErrorCode = Union[ErrorCodeGt, ErrorCodeLt]


class RawResponse(BaseModel):
    code: Literal[200]
    message: str
    data: str | dict


class ErrorResponse(BaseModel):
    code: ErrorCode
    message: str


ListT = TypeVar("ListT")


class GenericListData(GenericModel, Generic[ListT]):
    page: int
    pageCount: int
    list: List[ListT] = Field(default_factory=list)


class AccessTokenData(BaseModel):
    accessToken: str
    expires: int
    refreshToken: str
    openId: str
    unionId: str


class UserInfo(BaseModel):
    avatar: str
    nickname: str
    phone: str


class UserInfoData(BaseModel):
    userInfo: UserInfo


class UserCollection(BaseModel):
    accessToken: str
    expires: int
    refreshToken: str
    openId: str
    unionId: str


UserCollectionListData: TypeAlias = GenericListData[UserCollection]
