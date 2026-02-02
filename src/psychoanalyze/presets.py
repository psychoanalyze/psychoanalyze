"""Preset parameter configurations for common psychophysics paradigms.

This module provides named parameter sets for different experimental designs:
- Standard: Classic detection task with no guessing or lapsing
- Non-standard: Task with significant guess and lapse rates
- 2AFC: Two-alternative forced choice with 50% guess rate

Each preset defines the four psychometric function parameters:
- x_0: Threshold (stimulus intensity at 50% detection)
- k: Slope/steepness of the psychometric function
- gamma: Guess rate (lower asymptote)
- lambda: Lapse rate (1 - upper asymptote)

Additionally, each preset specifies which parameters are "free" (can be
estimated from data) vs "fixed" (held constant during fitting).
"""

from typing import TypedDict


class PresetParams(TypedDict):
    """Parameter values for a psychometric function preset."""

    x_0: float
    k: float
    gamma: float
    lambda_: float  # 'lambda' is a Python keyword


class PresetConfig(TypedDict):
    """Full configuration for a preset including params and free flags."""

    params: PresetParams
    free: dict[str, bool]
    description: str


# Parameter presets as dictionaries
PRESETS: dict[str, PresetParams] = {
    "standard": {
        "x_0": 0.0,
        "k": 1.0,
        "gamma": 0.0,
        "lambda_": 0.0,
    },
    "non-standard": {
        "x_0": 10.0,
        "k": 2.0,
        "gamma": 0.2,
        "lambda_": 0.1,
    },
    "2AFC": {
        "x_0": 0.0,
        "k": 1.0,
        "gamma": 0.5,
        "lambda_": 0.0,
    },
}

# Which parameters are free (estimable) for each preset
PRESET_FREE: dict[str, dict[str, bool]] = {
    "standard": {
        "x_0": True,
        "k": True,
        "gamma": True,
        "lambda_": True,
    },
    "non-standard": {
        "x_0": True,
        "k": True,
        "gamma": True,
        "lambda_": True,
    },
    "2AFC": {
        "x_0": True,
        "k": True,
        "gamma": False,  # Fixed at 0.5 for 2AFC
        "lambda_": True,
    },
}

# Full preset configurations with descriptions
PRESET_CONFIGS: dict[str, PresetConfig] = {
    "standard": {
        "params": PRESETS["standard"],
        "free": PRESET_FREE["standard"],
        "description": "Standard detection task with no guessing or lapsing",
    },
    "non-standard": {
        "params": PRESETS["non-standard"],
        "free": PRESET_FREE["non-standard"],
        "description": "Detection task with significant guess and lapse rates",
    },
    "2AFC": {
        "params": PRESETS["2AFC"],
        "free": PRESET_FREE["2AFC"],
        "description": "Two-alternative forced choice (50% guess rate fixed)",
    },
}


def get_preset(name: str) -> PresetParams:
    """Get parameter values for a named preset.

    Args:
        name: Preset name ('standard', 'non-standard', '2AFC')

    Returns:
        Dictionary of parameter values

    Raises:
        KeyError: If preset name is not found

    Example:
        >>> params = get_preset("standard")
        >>> params["x_0"]
        0.0
    """
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        msg = f"Unknown preset '{name}'. Available: {available}"
        raise KeyError(msg)
    return PRESETS[name]


def get_preset_free(name: str) -> dict[str, bool]:
    """Get free parameter flags for a named preset.

    Args:
        name: Preset name ('standard', 'non-standard', '2AFC')

    Returns:
        Dictionary mapping parameter names to whether they are free

    Raises:
        KeyError: If preset name is not found

    Example:
        >>> free = get_preset_free("2AFC")
        >>> free["gamma"]  # Fixed for 2AFC
        False
    """
    if name not in PRESET_FREE:
        available = ", ".join(PRESET_FREE.keys())
        msg = f"Unknown preset '{name}'. Available: {available}"
        raise KeyError(msg)
    return PRESET_FREE[name]


def get_preset_config(name: str) -> PresetConfig:
    """Get full configuration for a named preset.

    Args:
        name: Preset name ('standard', 'non-standard', '2AFC')

    Returns:
        Full preset configuration including params, free flags, and description

    Raises:
        KeyError: If preset name is not found

    Example:
        >>> config = get_preset_config("2AFC")
        >>> config["description"]
        'Two-alternative forced choice (50% guess rate fixed)'
    """
    if name not in PRESET_CONFIGS:
        available = ", ".join(PRESET_CONFIGS.keys())
        msg = f"Unknown preset '{name}'. Available: {available}"
        raise KeyError(msg)
    return PRESET_CONFIGS[name]


def list_presets() -> list[str]:
    """List all available preset names.

    Returns:
        List of preset names

    Example:
        >>> list_presets()
        ['standard', 'non-standard', '2AFC']
    """
    return list(PRESETS.keys())


def to_fitting_params(preset_params: PresetParams) -> dict[str, float]:
    """Convert preset params to fitting-compatible format.

    Renames 'lambda_' to 'lambda' for use with fitting functions.

    Args:
        preset_params: Parameters from a preset

    Returns:
        Dictionary with 'lambda' key instead of 'lambda_'

    Example:
        >>> params = get_preset("standard")
        >>> fitting_params = to_fitting_params(params)
        >>> "lambda" in fitting_params
        True
    """
    return {
        "x_0": preset_params["x_0"],
        "k": preset_params["k"],
        "gamma": preset_params["gamma"],
        "lambda": preset_params["lambda_"],
    }
