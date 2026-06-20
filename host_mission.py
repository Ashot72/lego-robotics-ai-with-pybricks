"""Stage mission scripts and parse hub RESULT lines."""

from __future__ import annotations

import re
from pathlib import Path

from template import mission_control

_MISSION_TEMPLATE = Path(mission_control.__file__)

MISSION_PARAMS: tuple[str, ...] = (
    "speed_green",
    "speed_yellow",
    "speed_blue",
    "speed_red",
    "turn_rate_green",
    "turn_rate_yellow",
    "turn_rate_blue",
    "turn_rate_red",
    "motor_d_speed",
)

DEFAULT_MISSION_PARAMS: dict[str, int] = {
    name: getattr(mission_control, name) for name in MISSION_PARAMS
}

_HOST_PARAMS_RE = re.compile(
    r"# --- HOST_PARAMS_START ---\r?\n.*?# --- HOST_PARAMS_END ---\r?\n",
    re.DOTALL,
)


def prepare_mission_control_run(generated_dir: str, params: dict[str, int]) -> str:
    """Inject mission params into the template and write to _generated/."""
    dst = Path(generated_dir) / _MISSION_TEMPLATE.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = _MISSION_TEMPLATE.read_text(encoding="utf-8")

    lines = ["# AI/Host will replace the variables below before upload"]
    for name in MISSION_PARAMS:
        lines.append(f"{name} = {params[name]}")
    params_block = "\n".join(lines) + "\n"
    if not _HOST_PARAMS_RE.search(text):
        raise ValueError(f"{_MISSION_TEMPLATE} is missing HOST_PARAMS block")

    text = _HOST_PARAMS_RE.sub(
        "# --- HOST_PARAMS_START ---\n" + params_block + "# --- HOST_PARAMS_END ---\n",
        text,
        count=1,
    )

    dst.write_text(text, encoding="utf-8")
    return str(dst)


def parse_hub_result(line: str) -> dict[str, str] | None:
    line = line.strip()
    if not line.startswith("RESULT "):
        return None

    result: dict[str, str] = {}
    for part in line[len("RESULT ") :].split():
        if "=" in part:
            key, value = part.split("=", 1)
            result[key] = value
    return result or None


def result_to_params(result: dict[str, str]) -> dict[str, int]:
    """Map hub RESULT keys to session param dict."""
    params = DEFAULT_MISSION_PARAMS.copy()
    for name in MISSION_PARAMS:
        if name in result:
            params[name] = int(result[name])
    return params
