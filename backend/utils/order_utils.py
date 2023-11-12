from backend.utils.snowflake import Snowflake, InvalidSystemClock

snowflake = Snowflake()


def get_order_id():
    return f"{snowflake.generate_id()}"


def get_goods_order_id():
    return f"G{get_order_id()}"
