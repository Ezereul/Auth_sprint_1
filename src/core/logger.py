from src.core.config import settings

LOGGING_DICT_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': settings.logger.format},
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s %(message)s',
            'use_colors': None,
        },
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': "%(asctime)s - uvicorn - %(client_addr)s - %(levelname)s - '%(request_line)s' %(status_code)s",
        },
    },
    'handlers': {
        'console': {
            'level': settings.logger.level_console,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'access': {
            'formatter': 'access',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': settings.logger.default_handlers,
            'level': settings.logger.level_handlers,
        },
        'uvicorn.error': {
            'level': settings.logger.level_unicorn_errors,
        },
        'uvicorn.access': {
            'handlers': ['access', ],
            'level': settings.logger.level_unicorn_access,
            'propagate': False,
        },
    },
    'root': {
        'level': settings.logger.level_root,
        'formatter': 'verbose',
        'handlers': settings.logger.default_handlers,
    },
}
