import logging
import pathlib
import sys
import tomllib

path = pathlib.Path(__file__).parent / "tastytrade.toml"
with path.open(mode="rb") as file:
    cfg = tomllib.load(file)

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)