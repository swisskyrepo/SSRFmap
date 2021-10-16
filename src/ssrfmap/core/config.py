from typing import Literal, Optional

import attr


@attr.s(slots=True)
class SsrfmapConfig:
    """SSRFmap Configuration"""

    reqfile: str = attr.ib()
    param: str = attr.ib()
    modules: list[str] = attr.ib()
    handler: Optional[str] = attr.ib(default=None)
    verbose: Optional[bool] = attr.ib(default=False)
    lhost: Optional[str] = attr.ib(default=None)
    lport: Optional[int] = attr.ib(default=None)
    targetfiles: Optional[list[str]] = attr.ib(default=None)
    useragent: Optional[str] = attr.ib(default="")
    ssl: Optional[bool] = attr.ib(default=True)
    level: Optional[Literal[1, 2, 3, 4, 5]] = attr.ib(default=1)
