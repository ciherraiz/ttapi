import pathlib
import tomllib

path = pathlib.Path(__file__).parent / "tastytrade.toml"
with path.open(mode="rb") as file:
    tastytrade = tomllib.load(file)