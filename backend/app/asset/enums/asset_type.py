from enum import Enum


class AssetType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    BROLL = "broll"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    FONT = "font"
    SUBTITLE_STYLE = "subtitle_style"
    MOTION_PRESET = "motion_preset"
    TRANSITION = "transition"
    LUT = "lut"
    INTRO = "intro"
    OUTRO = "outro"
    STICKER = "sticker"
    CTA = "cta"
    TEMPLATE = "template"
    BRAND_KIT = "brand_kit"