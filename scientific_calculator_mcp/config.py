import logging

MAX_EXPRESSION_LENGTH = 512
DEFAULT_PRECISION = 10
MIN_PRECISION = 0
MAX_PRECISION = 15
DEFAULT_ANGLE_MODE = "radians"
SUPPORTED_ANGLE_MODES = {"radians", "degrees"}


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
