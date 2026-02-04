"""Feature flags for experimental functionality.

This module provides a centralized way to control experimental features
using environment variables.

Feature Flags:
    PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING: When set to "1" or "true",
        enables adaptive sampling methods (BOED). Default is disabled.

Example:
    Enable adaptive sampling via environment variable:

    .. code-block:: bash

        export PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING=1

    Or in Python:

    .. code-block:: python

        import os
        os.environ["PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING"] = "1"

        from psychoanalyze.features import is_adaptive_sampling_enabled
        if is_adaptive_sampling_enabled():
            # Use BOED sampling
            ...
"""

import os


def _parse_bool_env(name: str, *, default: bool = False) -> bool:
    """Parse a boolean environment variable.

    Args:
        name: Environment variable name.
        default: Default value if not set.

    Returns:
        True if env var is set to "1", "true", or "yes" (case insensitive).
    """
    value = os.environ.get(name, "").lower()
    if value in ("1", "true", "yes", "on"):
        return True
    if value in ("0", "false", "no", "off"):
        return False
    return default


def is_adaptive_sampling_enabled() -> bool:
    """Check if adaptive sampling methods are enabled.

    Adaptive sampling methods (e.g., BOED - Bayesian Optimal Experimental Design)
    are experimental and hidden behind this feature flag.

    Returns:
        True if PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING is set to "1" or "true".
    """
    return _parse_bool_env("PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING", default=False)
