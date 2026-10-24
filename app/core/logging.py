import logging

from asgi_correlation_id import CorrelationIdFilter


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(correlation_id)s] %(name)s %(message)s",
    )
    for handler in logging.getLogger().handlers:
        handler.addFilter(CorrelationIdFilter(default_value="-"))
