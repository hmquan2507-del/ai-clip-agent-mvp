from __future__ import annotations


class OpenAIProviderError(Exception):
    pass


class OpenAIConfigurationError(OpenAIProviderError):
    pass