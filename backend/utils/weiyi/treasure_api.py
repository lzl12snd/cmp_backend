from __future__ import annotations

import requests
import hashlib
from pydantic import BaseModel, ConstrainedInt, ValidationError, Field
from loguru import logger
from typing import Literal

# https://www.weiyi.art/help/second/ebb5ab56726e451db01434bd35376420/9fa0f68a891a427aa2437dc702e08049

url = "http://qa-api.theone.art/verify-treasure/api/app/treasure/verifyUser"
app_id = "PX1BASi3NU8k7gOM"
app_key = "jfaO2wXD8zDcDh72nN8OYKoMWdKkY3Lz"


class TreasureDetail(BaseModel):
    name: str
    commodityUuid: str
    number: int
    cover: str = Field(..., repr=False)
    typeMarket: int
    # categoryName: str
    # categoryImage: str


# {
#     "number": 2,
#     "name": "橙芒分类测试商品1",
#     "commodityUuid": "29ce77debbbb73c6bf9a587364a1c7ce",
#     "cover": "https://qa-theoneart-public-shenzhen.oss-cn-shenzhen.aliyuncs.com/watermarkResize/98ce2221777449433b7cc6dbf444c86a/4ce65675d7467f861ede1d2df4f35272-16977025629740.9.jpg",
#     "typeMarket": 2,
#     "categoryName": "橙芒",
#     "categoryImage": "https://qa-theoneart-public-shenzhen.oss-cn-shenzhen.aliyuncs.com/watermarkResize/98ce2221777449433b7cc6dbf444c86a/4ce65675d7467f861ede1d2df4f35272-16977025629740.9.jpg",
#     "tokenId": null,
#     "contractAddress": null,
#     "chainContract": null,
#     "chainName": null
# }

# treasureDetail
# 参数名	参数值	备注
# number	10001	编号
# name	仙剑一	商品名
# commodityUuid  29ce77debbbb73c6bf9a587364a1c7ce  商品唯一标识
# cover	 	图片url
# typeMarket	 	市场类型：1 版权品 2 衍生品 3 数字身份
# categoryName	 	分类名称
# categoryImage	 	分类封面图
# tokenId	 	认证标识
# contractAddress	 	合约地址
# chainContract	 	认证标准
# chainName	 	认证网络


class ErrorCodeGt(ConstrainedInt):
    gt = 200


class ErrorCodeLt(ConstrainedInt):
    lt = 200


ErrorCode = ErrorCodeGt | ErrorCodeLt


class ErrorResponse(BaseModel):
    code: ErrorCode
    message: str


class TreasureData(BaseModel):
    totalCount: int
    treasureDetails: list[TreasureDetail] | None = None


class ResponseModel(BaseModel):
    code: Literal[200]
    message: str
    data: dict


def encode_params(params: dict, key: str) -> str:
    s = []
    for k, v in sorted(params.items()):
        s.append(f"{k}={v}")
    s.append(f"key={key}")
    return "&".join(s)


def get_user_treasure(phone: str, commodity_name: str | None = None):
    treasure_list: list[TreasureDetail] = []
    page_size = 10
    max_page = 50
    now_page = 0
    while True:
        # 参数名	参数值	是否必传	备注
        # appId	testappId	是	商户id
        # phone	133055333923	是	用户手机号
        # commodityName	商品名	否	商品名称 选传
        # categoryId	分类id	否	分类id 范围接口返回 选传
        # pageCount	页码	否	分页页码 不传默认为1
        # sourceTypes	来源	否	不传默认是全部 2购买 3空投 4补发 5盲盒 6赠与 数据格式 ,分割的字符串 例如 1）购买 2; 2）空投+盲盒：3,5
        # type	类型	否	 1：版权品，2：衍生品，3：数字身份
        now_page += 1
        params = {
            "appId": app_id,
            "phone": phone,
            "pageCount": now_page,
        }
        if commodity_name:
            params["commodityName"] = commodity_name

        str_to_sign = encode_params(params, key=app_key)
        sign = hashlib.md5(str_to_sign.encode()).hexdigest().upper()

        response = requests.post(url, json={**params, "sign": sign})
        if not response.ok:
            logger.warning(response.text)
            raise ValueError(f"请求失败: {response.status_code}")
        try:
            raw = ResponseModel.parse_raw(response.text)
            data = TreasureData.parse_obj(raw.data)
        except ValidationError:
            try:
                err_resp = ErrorResponse.parse_raw(response.text)
                raise ValueError(err_resp.message)
            except ValidationError:
                logger.warning(response.text)
                raise ValueError("解析错误")

        if not data.treasureDetails:
            break
        treasure_list.extend(data.treasureDetails)
        if len(treasure_list) < 10:
            break
        if now_page * page_size == data.totalCount:
            break
        if now_page >= max_page:
            break

    return treasure_list
