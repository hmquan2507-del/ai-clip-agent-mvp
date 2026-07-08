from enum import Enum


class ProviderKey(str, Enum):
    LOCAL = "local"
    INTERNAL = "internal"
    USER_UPLOAD = "user_upload"
    PEXELS = "pexels"
    PIXABAY = "pixabay"
    FREESOUND = "freesound"
    ARTLIST = "artlist"
    EPIDEMIC = "epidemic"
    GOOGLE_FONT = "google_font"