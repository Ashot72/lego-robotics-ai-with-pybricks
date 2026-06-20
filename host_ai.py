"""OpenAI natural-language parsing for mission host parameters."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from host_mission import MISSION_PARAMS

load_dotenv()

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You configure a LEGO Boost Move Hub color-following mission.

Return ALL 9 parameters every time. Copy unchanged values from current_params.
Only change fields the user explicitly mentions.

Parameters:
- speed_green, speed_yellow, speed_blue, speed_red — drive speed per color (red 0 = stop)
- turn_rate_green, turn_rate_yellow, turn_rate_blue, turn_rate_red — turn deg/s per color
- motor_d_speed — port D motor speed

Limits: speeds and motor_d_speed -500 to 500, turn rates -360 to 360 (negative = reverse).
List changed param keys in "changed". Short "reply" for the user.
"""


class MissionParams(BaseModel):
    speed_green: int
    speed_yellow: int
    speed_blue: int
    speed_red: int
    turn_rate_green: int
    turn_rate_yellow: int
    turn_rate_blue: int
    turn_rate_red: int
    motor_d_speed: int


class MissionIntent(BaseModel):
    params: MissionParams
    changed: list[str] = Field(default_factory=list)
    reply: str


def _param_limit(param_key: str) -> tuple[int, int]:
    return (-360, 360) if "turn_rate" in param_key else (-500, 500)


def _validate_params(params: dict[str, int]) -> dict[str, int]:
    for name in MISSION_PARAMS:
        lo, hi = _param_limit(name)
        value = int(params[name])
        if value < lo or value > hi:
            raise ValueError(f"{name}={value} out of range [{lo}, {hi}]")
    return params


def _build_user_message(user_text: str, current_params: dict[str, int]) -> str:
    payload: dict[str, Any] = {
        "current_params": current_params,
        "user_text": user_text,
    }
    return json.dumps(payload, indent=2)


def parse_mission_prompt(
    user_text: str,
    current_params: dict[str, int],
) -> MissionIntent:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set — add it to .env")

    client = OpenAI(api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_user_message(user_text, current_params),
            },
        ],
        response_format=MissionIntent,
    )

    message = completion.choices[0].message
    if message.parsed is None:
        raise RuntimeError("OpenAI did not return structured mission params")

    intent = message.parsed
    _validate_params(intent.params.model_dump())
    return intent
