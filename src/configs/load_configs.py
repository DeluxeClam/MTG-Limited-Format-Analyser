import yaml
from dataclasses import dataclass

@dataclass
class EnvironmentConfig:
    name: str
    set_code: str
    environment_type: str
    layers: list[str]
    exposure_method: str


def load_config(path):
    with open(path) as f:
        config_dict = yaml.safe_load(f)

    return EnvironmentConfig(
        name=config_dict.get("name"),
        set_code=config_dict.get("set_code"),
        environment_type=config_dict.get("type"),
        layers=config_dict.get("graph").get("layers"),
        exposure_method=config_dict.get("exposure").get("method")
    )
