"""
PC host for LegoBoost — natural-language mission control via OpenAI.

Type plain English at the prompt; params sync from hub RESULT after deploy.
  s = stop hub program   q = quit
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from host_ai import parse_mission_prompt
from host_mission import (
    DEFAULT_MISSION_PARAMS,
    parse_hub_result,
    prepare_mission_control_run,
    result_to_params,
)

GENERATED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_generated")

HUB_TIPS = """
Hub not found. Check: hub ON, Pybricks firmware, Boost app closed, Bluetooth on.
Try: host.bat -n "Pybricks Hub" --timeout 60
"""

HELP_TEXT = (
    "Type mission changes in plain English.  s=stop  q=quit\n"
    "Baseline: defaults (first time) or last hub RESULT / upload.\n"
    f"Defaults: {DEFAULT_MISSION_PARAMS}"
)


class MissionState:
    def __init__(self) -> None:
        self.current_params = DEFAULT_MISSION_PARAMS.copy()
        self._lock = asyncio.Lock()
        self._reader_task: asyncio.Task | None = None

    async def snapshot(self) -> dict[str, int]:
        async with self._lock:
            return self.current_params.copy()

    async def apply_result(self, result: dict[str, str]) -> None:
        async with self._lock:
            self.current_params = result_to_params(result)


async def _stop_reader(state: MissionState) -> None:
    if state._reader_task is None:
        return
    state._reader_task.cancel()
    try:
        await state._reader_task
    except asyncio.CancelledError:
        pass
    state._reader_task = None


async def _hub_line_reader(hub, state: MissionState) -> None:
    try:
        while True:
            try:
                line = await hub.read_line()
            except Exception:
                break
            if not line.strip():
                continue
            result = parse_hub_result(line)
            if result:
                await state.apply_result(result)
                params = await state.snapshot()
                print(f"Hub RESULT: {params}", flush=True)
    except asyncio.CancelledError:
        raise


async def _run_mission(hub, state: MissionState, params: dict[str, int]) -> None:
    await _stop_reader(state)
    await hub.stop_user_program()

    path = prepare_mission_control_run(GENERATED_DIR, params)
    print(f"Uploading: {params}", flush=True)
    await hub.run(path, wait=False, print_output=False, line_handler=True)
    print("Deployed.", flush=True)
    async with state._lock:
        state.current_params = params.copy()
    state._reader_task = asyncio.create_task(_hub_line_reader(hub, state))


async def _handle_stop(hub, state: MissionState) -> None:
    await _stop_reader(state)
    await hub.stop_user_program()
    print("stopped", flush=True)


async def _handle_prompt(hub, state: MissionState, user_text: str) -> None:
    current_params = await state.snapshot()
    intent = await asyncio.to_thread(
        parse_mission_prompt,
        user_text,
        current_params,
    )
    print(f"AI: {intent.reply}", flush=True)
    if intent.changed:
        print(f"Changed: {', '.join(intent.changed)}", flush=True)
    await _run_mission(hub, state, intent.params.model_dump())


_LOCAL_COMMANDS = {"q": "quit", "quit": "quit", "s": "stop", "stop": "stop"}


def _is_local_command(line: str) -> str | None:
    return _LOCAL_COMMANDS.get(line.strip().lower())


async def _run_host(hub_name: str | None, timeout: float) -> int:
    from pybricksdev.ble import find_device
    from pybricksdev.connections.pybricks import PybricksHubBLE

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set — copy .env.example to .env and add your key.", flush=True)
        return 1

    print(f"Searching for hub ({timeout:.0f} s)...")
    try:
        device = await find_device(hub_name, timeout=timeout)
    except asyncio.TimeoutError:
        print(HUB_TIPS)
        return 1

    hub = PybricksHubBLE(device)
    await hub.connect()
    state = MissionState()

    print("Connected.")
    print(HELP_TEXT)
    print()

    try:
        await _run_mission(hub, state, state.current_params)
    except Exception as exc:
        print(f"Deploy failed: {exc}", flush=True)
        await _stop_reader(state)
        await hub.disconnect()
        return 1

    try:
        while True:
            line = await asyncio.to_thread(input, "> ")
            line = line.strip()
            if not line:
                continue

            local = _is_local_command(line)
            if local in ("stop", "quit"):
                try:
                    await _handle_stop(hub, state)
                except Exception as exc:
                    print(f"failed: {exc}", flush=True)
                if local == "quit":
                    break
                continue

            try:
                await _handle_prompt(hub, state, line)
            except Exception as exc:
                print(f"failed: {exc}", flush=True)

        return 0
    except KeyboardInterrupt:
        return 130
    finally:
        await _stop_reader(state)
        await hub.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(description="LegoBoost OpenAI mission host")
    parser.add_argument("-n", "--name", help="Bluetooth hub name")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    return asyncio.run(_run_host(args.name, args.timeout))


if __name__ == "__main__":
    sys.exit(main())
