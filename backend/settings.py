"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urljoin

import redis

os.environ["LOGURU_AUTOINIT"] = "0"
os.environ["LOGURU_LEVEL"] = "INFO"

import loguru

BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = Path(__file__).resolve().parent / "apps"
sys.path.insert(0, str(APPS_DIR))

LOG_DIR = BASE_DIR / "logs"
LOG_FILE_PATH = LOG_DIR / "run.log"
DIST_ROOT = BASE_DIR / "dist"
STATIC_ROOT = DIST_ROOT / "static"
MEDIA_ROOT = BASE_DIR / "media"


# 阿里云 OSS
OSS_ACCESS_KEY_ID = ""
OSS_ACCESS_KEY_SECRET = ""
# https://help.aliyun.com/document_detail/31837.html
OSS_REGION = "oss-cn-hangzhou"
OSS_ENDPOINT = f"{OSS_REGION}.aliyuncs.com"
OSS_BUCKET_NAME = ""


# 腾讯云 COS
COS_SECRET_ID = ""
COS_SECRET_KEY = ""
# https://cloud.tencent.com/document/product/436/6224
COS_REGION = "ap-shanghai"
COS_ENDPOINT = f"cos.{COS_REGION}.myqcloud.com"
COS_BUCKET = ""
COS_APPID = ""
COS_BUCKET_APPID = f"{COS_BUCKET}-{COS_APPID}"


for path in [LOG_DIR, STATIC_ROOT, MEDIA_ROOT, APPS_DIR]:
    if not path.exists():
        path.mkdir(parents=True)

# DOMAIN_NAME = "43.137.46.100"
DOMAIN_NAME = "mall.gamefi01.art"
# DOMAIN_NAME = "mall.bigera.games"
BASE_URL = f"https://{DOMAIN_NAME}"

UWSGI_INI_FILE_NAME = DOMAIN_NAME  # uwsgi配置文件名
CRONTAB_COMMENT = "cmp"  # django-crontab 注释, 区分不同项目
DB_PREFIX = "cmp"  # 数据库表名前缀
REDIS_PREFIX = "cmp"  # redis前缀
DEFAULT_AVATAR = urljoin(BASE_URL, "media/default_avatar.svg")
DEFAULT_AVATAR_BACK = urljoin(BASE_URL, "media/default_avatar.svg")


def get_redis_connection() -> redis.Redis:
    redis_conn = redis.Redis(
        host="10.206.0.17",
        port=6379,
        db=1,
        decode_responses=True,
    )
    return redis_conn


# https://github.com/Delgan/loguru#suitable-for-scripts-and-libraries
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


if sys.version_info >= (3, 8):
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
else:
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

loguru.logger.add(
    LOG_DIR / "run.log",
    level=logging.INFO,
    filter=lambda record: record["extra"].get("name") is None,
    backtrace=False,
    watch=True,
)

LOGURU_LOGGERS_CACHE: Dict[str, "loguru.Logger"] = {}


def get_logger(name: Optional[str] = None):
    if name is None:
        return loguru.logger
    if name in LOGURU_LOGGERS_CACHE:
        return LOGURU_LOGGERS_CACHE[name]

    bind_logger = loguru.logger.bind(name=name)
    bind_logger.add(
        LOG_DIR / f"{name}.log",
        level=logging.INFO,
        filter=lambda record: record["extra"].get("name") == name,
        backtrace=False,
        watch=True,
    )

    LOGURU_LOGGERS_CACHE[name] = bind_logger
    return bind_logger


def redirect_default_logger(name: str, keep_default: bool):
    if not keep_default:
        loguru.logger.remove()

    loguru.logger.add(
        LOG_DIR / f"{name}.log",
        backtrace=False,
        watch=True,
    )
    return loguru.logger


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "7h^ou-2%-vufqhu2y#1wu+n*m4(fat#7s@^0iv9&#n=u5yl(31"
if "django-insecure" in SECRET_KEY:
    loguru.logger.warning("SECRET_KEY is insecure! Please run `python manage.py generate_secret_key` to generate a new one.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    # 增加 ninja 后不用cdn, 使用静态资源
    # 需要python manage.py collectstatic
    "ninja",
    "django_extensions",
    # "django_crontab",
    "back",
    "user",
    "openapi",
    "order",
    "goods",
]

MIDDLEWARE = [
    # "backend.utils.middlewares.ApiLoggingMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": "10.206.0.15",
        "PORT": 3306,
        "USER": "root",
        "PASSWORD": "mate=Portalverse1",
        "NAME": "cmp_db",
        "OPTIONS": {"charset": "utf8mb4"},
        "CONN_MAX_AGE": 720,
    },
}


# 跨域增加忽略
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
    "VIEW",
)

CORS_ALLOW_HEADERS = (
    "Authorization",
    "XMLHttpRequest",
    "X_FILENAME",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "Pragma",
)


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "zh-Hans"

TIME_ZONE = "Asia/Shanghai"

DATETIME_FORMAT = "Y-m-d H:i:s"

USE_I18N = True


# 国际化翻译
# https://docs.djangoproject.com/zh-hans/4.2/topics/i18n/translation/
# 添加django.middleware.locale.LocaleMiddleware
# https://docs.djangoproject.com/zh-hans/4.2/topics/i18n/translation/#how-django-discovers-language-preference
# 创建语言文件
# https://docs.djangoproject.com/zh-hans/4.2/topics/i18n/translation/#localization-how-to-create-language-files
# python manage.py makemessages -l en -l es -l fr -l ko -l ja -l pt -l zh_Hans -l zh_Hant --ignore=venv/*
# python manage.py compilemessages --ignore=venv/*

# LOCALE_PATHS = [
#     BASE_DIR / "locale",
# ]

USE_L10N = True

USE_TZ = False


# 表达式生成
# https://crontab.guru/examples.html
# 添加定时任务
# python manage.py crontab add
# 清除定时任务
# python manage.py crontab remove
# 显示定时任务
# python manage.py crontab show

CRONJOBS = [
    # ("0 0 * * *", "backend.utils.mail.send_email"),
    # ("0 0 * * *", "backend.utils.mail.check_email", ">> logs/crontab.log"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "static/"

MEDIA_URL = urljoin(BASE_URL, "media/")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
