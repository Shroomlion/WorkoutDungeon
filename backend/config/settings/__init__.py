from decouple import config

match config("ENVIRONMENT", default="dev"):
    case "prod":
        from .prod import *
    case _:
        from .dev import *
