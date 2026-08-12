"""Configuration loading for Go2 control."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib
from typing import Any


@dataclass(slots=True)
class Go2Config:
    """User-editable settings for the robot control tools."""

    robot_ip: str = "192.168.12.1"
    wifi_name: str = "UNITREE_GO2"
    default_walk_speed_mps: float = 0.1


DEFAULT_CONFIG_PATH = Path("go2_config.toml")
DEFAULT_GO2_CONFIG = Go2Config()


def _env_value(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


def _env_float(name: str) -> float | None:
    raw_value = _env_value(name)
    if raw_value is None:
        return None
    return float(raw_value)


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> Go2Config:
    """Load config from TOML, then apply environment overrides."""

    config_path = Path(path)
    config = Go2Config()

    if config_path.exists():
        with config_path.open("rb") as handle:
            raw_data = tomllib.load(handle)

        go2_data: dict[str, Any] = raw_data.get("go2", {})
        config = Go2Config(
            robot_ip=str(go2_data.get("robot_ip", config.robot_ip)),
            wifi_name=str(go2_data.get("wifi_name", config.wifi_name)),
            default_walk_speed_mps=float(go2_data.get("default_walk_speed_mps", config.default_walk_speed_mps)),
        )

    default_walk_speed = _env_float("GO2_DEFAULT_WALK_SPEED_MPS")

    return Go2Config(
        robot_ip=_env_value("GO2_ROBOT_IP") or config.robot_ip,
        wifi_name=_env_value("GO2_WIFI_NAME") or config.wifi_name,
        default_walk_speed_mps=default_walk_speed if default_walk_speed is not None else config.default_walk_speed_mps,
    )
