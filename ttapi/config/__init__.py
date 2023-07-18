import logging
import pathlib
import tomllib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_handler = logging.StreamHandler()
log_handler.setLevel(logging.DEBUG)

log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_format)

logger.addHandler(log_handler)

path = pathlib.Path(__file__).parent / "tastytrade.toml"
with path.open(mode="rb") as file:
    tastytrade = tomllib.load(file)