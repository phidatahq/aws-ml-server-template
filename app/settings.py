from typing import List, Optional

from pydantic import BaseSettings, validator


class AppSettings(BaseSettings):
    """App settings from container environment.

    Reference: https://pydantic-docs.helpmanual.io/usage/settings/
    """

    # App runtime derived from the `runtime` environment variable.
    # Valid values include "dev", "stg", "prd"
    runtime: str = "dev"

    secret_key: Optional[str]
    docs_enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 9090

    # Cors origin list to allow requests from. This list is derived from the runtime.
    cors_origin_list: Optional[List[str]] = None

    @validator("cors_origin_list", always=True)
    def set_cors_origin_list(cls, cors_origin_list, values):
        valid_cors = cors_origin_list or []

        runtime = values.get("runtime")
        if runtime == "dev":
            # 3000 is the default port for create-react-app
            valid_cors.extend(["http://localhost:3000"])

        return valid_cors
