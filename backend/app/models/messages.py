from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ChannelCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    channel_type: str = Field(default="team", max_length=32)
    description: Optional[str] = Field(default=None, max_length=240)


class MessageCreate(BaseModel):
    content: str = Field(default="", max_length=4000)
    message_type: str = Field(default="text", max_length=32)
    gif_url: Optional[str] = None
    reply_to_id: Optional[str] = None
    file_ids: list[str] = Field(default_factory=list, max_length=5)
    sender_name: Optional[str] = Field(default=None, max_length=80)


class AskInChannelBody(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class ReactBody(BaseModel):
    emoji: str
