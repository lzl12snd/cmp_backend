import base64
from typing import TypeVar
from urllib.parse import urlencode, urljoin

import requests
from loguru import logger
from pydantic import BaseModel

from .crypt import RsaCipher
from .models import (
    AccessTokenData,
    ErrorResponse,
    RawResponse,
    UserCollectionListData,
    UserInfo,
    UserInfoData,
)

# https://www.weiyi.art/help/second/86a2970d2b7f4e1b8e796db15f3bacce/730df6531a054b88af044f833fd1af3a


DataT = TypeVar("DataT", bound=BaseModel)


class WeiyiClient:
    def __init__(
        self,
        app_id: str,
        app_key: str,
        cipher: RsaCipher,
        scopes: list[str],
        redirect_uri: str,
        base_url: str,
        api_base_url: str,
    ):
        self.app_id = app_id
        self.app_key = app_key
        self.cipher = cipher
        self.scopes = scopes
        self.redirect_uri = redirect_uri
        self.base_url = base_url
        self.api_base_url = api_base_url

    def __try_response_get_data(self, response: requests.Response, model: type[DataT]) -> DataT:
        if not response.ok:
            logger.warning(response.text)
            raise ValueError(f"请求失败: {response.status_code}")
        try:
            raw_response = RawResponse.parse_raw(response.text)
            datadata_bytes = base64.b64decode(raw_response.data)
            data_decrypted = self.cipher.decrypt(datadata_bytes)
            return model.parse_raw(data_decrypted)
        except Exception as e:
            logger.warning(response.text)
            try:
                raise ValueError(ErrorResponse.parse_raw(response.text).message)
            except Exception:
                pass
            raise ValueError(f"解析错误: {e}")

    def get_authorization_url(self) -> str:
        """获取授权登录页"""
        params = urlencode(
            {
                "appId": self.app_id,
                "scope": ",".join(self.scopes),
                "redirectUri": self.redirect_uri,
            }
        )
        authorization_url = urljoin(self.base_url, "Authorize")
        return f"{authorization_url}?{params}"

    def get_access_token(self, code: str) -> AccessTokenData:
        """换取访问凭证"""
        response = requests.post(
            urljoin(self.api_base_url, "/oauth/api/oauth2/accesstoken"),
            json={
                "appId": self.app_id,
                "secret": self.app_key,
                "code": code,
            },
        )

        return self.__try_response_get_data(response, AccessTokenData)

    def refresh_token(self, refresh_token: str) -> AccessTokenData:
        """刷新访问凭证"""
        response = requests.post(
            urljoin(self.api_base_url, "/oauth/api/oauth2/refreshtoken"),
            json={
                "appId": self.app_id,
                "refreshToken": refresh_token,
            },
        )
        return self.__try_response_get_data(response, AccessTokenData)

    def get_user_base_info(self, access_token: str) -> UserInfo:
        """获取用户信息"""
        response = requests.post(
            urljoin(self.api_base_url, "/oauth/api/gtw/user_base_info"),
            params={
                "accessToken": access_token,
            },
        )
        return self.__try_response_get_data(response, UserInfoData).userInfo

    def get_user_position_list(self, page: int, page_size: int, access_token: str) -> UserCollectionListData:
        """获取用户藏品列表"""
        response = requests.post(
            urljoin(self.api_base_url, "/oauth/api/gtw/user_position_list"),
            params={
                "accessToken": access_token,
            },
            json={
                "page": page,
                "pageSize": page_size,
            },
        )
        return self.__try_response_get_data(response, UserCollectionListData)
