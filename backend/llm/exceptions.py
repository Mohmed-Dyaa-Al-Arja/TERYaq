"""LLM-specific exceptions."""


class TeryaqLLMError(Exception):
    """Base error for the Teryaq LLM layer."""


class LLMConfigurationError(TeryaqLLMError):
    """Raised when required configuration is missing."""


class LLMGenerationError(TeryaqLLMError):
    """Raised when model generation fails."""


class InvalidLLMResponseError(TeryaqLLMError):
    """Raised when the model does not return valid structured output."""
