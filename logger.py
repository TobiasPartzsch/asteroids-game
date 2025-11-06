import inspect
import json
import math
from dataclasses import asdict
from datetime import datetime
from typing import Any, cast

import pygame

from game_models import Event, GameStateEntry, GroupLogInfo, SpriteLogInfo
from logging_protocols import (
    SpriteWithPosition,
    SpriteWithRadius,
    SpriteWithRotation,
    SpriteWithVelocity,
)

__all__ = ["log_state", "log_event"]

_FPS = 60
_MAX_SECONDS = 16
_SPRITE_SAMPLE_LIMIT = 10  # Maximum number of sprites to log per group

_frame_count = 0
_state_log_initialized = False
_event_log_initialized = False
_start_time = datetime.now()

SPRITE_POSITION = "position"
SPRITE_VELOCITY = "velocity"
SPRITE_RADIUS = "radius"
SPRITE_ROTATION = "rotation"


def log_state():
    global _frame_count, _state_log_initialized

    # Stop logging after `_MAX_SECONDS` seconds
    if _frame_count > _FPS * _MAX_SECONDS:
        return

    # Take a snapshot approx. once per second
    _frame_count += 1
    if _frame_count % _FPS:
        return

    now = datetime.now()

    frame = inspect.currentframe()
    if frame is None:
        return

    frame_back = frame.f_back
    if frame_back is None:
        return

    local_vars: dict[str, Any] = frame_back.f_locals.copy()

    screen_size: list[int] = []
    game_entities_to_log: dict[str, GroupLogInfo | SpriteLogInfo] = {}

    for key, value in local_vars.items():
        if isinstance(value, pygame.Surface):
            screen_size = list(value.get_size())

        if isinstance(value, pygame.sprite.Group):
            typed_sprite_group = cast(pygame.sprite.Group[Any], value)
            sprites_data: list[SpriteLogInfo] = []

            for i, item_from_group in enumerate(typed_sprite_group):
                if i >= _SPRITE_SAMPLE_LIMIT:
                    break

                sprite = cast(pygame.sprite.Sprite, item_from_group)
                current_sprite_log = SpriteLogInfo(type=sprite.__class__.__name__)

                if hasattr(sprite, SPRITE_POSITION):
                    positioned_sprite = cast(SpriteWithPosition, sprite)
                    current_sprite_log.pos = [
                        round(positioned_sprite.position.x, 2),
                        round(positioned_sprite.position.y, 2),
                    ]

                if hasattr(sprite, SPRITE_VELOCITY):
                    velocitied_sprite = cast(SpriteWithVelocity, sprite)
                    current_sprite_log.vel = [
                        round(velocitied_sprite.velocity.x, 2),
                        round(velocitied_sprite.velocity.y, 2),
                    ]

                if hasattr(sprite, SPRITE_RADIUS):
                    radius_sprite = cast(SpriteWithRadius, sprite)
                    current_sprite_log.rad = radius_sprite.radius

                if hasattr(sprite, SPRITE_ROTATION):
                    rotated_sprite = cast(SpriteWithRotation, sprite)
                    current_sprite_log.rot = round(rotated_sprite.rotation, 2)

                sprites_data.append(current_sprite_log)

            game_entities_to_log[key] = GroupLogInfo(
                count=len(typed_sprite_group), sprites=sprites_data
            )

        elif len(game_entities_to_log) == 0:
            single_sprite_log = SpriteLogInfo(type=value.__class__.__name__)

            if hasattr(value, SPRITE_POSITION):
                positioned_sprite = cast(SpriteWithPosition, value)
                single_sprite_log.pos = [
                    round(positioned_sprite.position.x, 2),
                    round(positioned_sprite.position.y, 2),
                ]

            if hasattr(value, SPRITE_VELOCITY):
                velocitied_sprite = cast(SpriteWithVelocity, value)
                single_sprite_log.vel = [
                    round(velocitied_sprite.velocity.x, 2),
                    round(velocitied_sprite.velocity.y, 2),
                ]

            if hasattr(value, SPRITE_RADIUS):
                radius_sprite = cast(SpriteWithRadius, value)
                single_sprite_log.rad = float(radius_sprite.radius)

            if hasattr(value, SPRITE_ROTATION):
                rotated_sprite = cast(SpriteWithRotation, value)
                single_sprite_log.rot = round(float(rotated_sprite.rotation), 2)

            game_entities_to_log[key] = single_sprite_log

    entry_dataclass = GameStateEntry(
        timestamp=now.strftime("%H:%M:%S.%f")[:-3],
        elapsed_s=math.floor((now - _start_time).total_seconds()),
        frame=_frame_count,
        screen_size=screen_size,
        game_entities=game_entities_to_log,
    )

    mode = "w" if not _state_log_initialized else "a"
    with open("game_state.jsonl", mode) as f:
        f.write(json.dumps(asdict(entry_dataclass)) + "\n")

    _state_log_initialized = True


def log_event(event_type: str, **details: dict[str, Any]):
    global _event_log_initialized

    now = datetime.now()

    event = Event(
        timestamp=now.strftime("%H:%M:%S.%f")[:-3],
        elapsed_s=math.floor((now - _start_time).total_seconds()),
        frame=_frame_count,
        type=event_type,
    )

    mode = "w" if not _event_log_initialized else "a"
    with open("game_events.jsonl", mode) as f:
        f.write(json.dumps(asdict(event)) + "\n")

    _event_log_initialized = True
