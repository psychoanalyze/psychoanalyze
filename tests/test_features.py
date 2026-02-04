"""Tests for psychoanalyze.features module."""

import os

import pytest

from psychoanalyze.data.trials import (
    AdaptiveSamplingDisabledError,
    generate,
)
from psychoanalyze.features import is_adaptive_sampling_enabled

# Number of trials used in tests
N_TRIALS = 10


def test_is_adaptive_sampling_enabled_default_false():
    """Feature flag is disabled by default."""
    # Ensure env var is not set
    os.environ.pop("PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING", None)
    assert is_adaptive_sampling_enabled() is False


def test_is_adaptive_sampling_enabled_when_set_to_1():
    """Feature flag is enabled when set to '1'."""
    os.environ["PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING"] = "1"
    try:
        assert is_adaptive_sampling_enabled() is True
    finally:
        os.environ.pop("PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING", None)


def test_is_adaptive_sampling_enabled_when_set_to_true():
    """Feature flag is enabled when set to 'true'."""
    os.environ["PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING"] = "true"
    try:
        assert is_adaptive_sampling_enabled() is True
    finally:
        os.environ.pop("PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING", None)


def test_is_adaptive_sampling_enabled_when_set_to_false():
    """Feature flag is disabled when explicitly set to 'false'."""
    os.environ["PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING"] = "false"
    try:
        assert is_adaptive_sampling_enabled() is False
    finally:
        os.environ.pop("PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING", None)


def test_boed_sampling_raises_when_flag_disabled():
    """BOED sampling raises error when feature flag is disabled."""
    os.environ.pop("PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING", None)

    params = {"x_0": 0.0, "k": 1.0, "gamma": 0.0, "lambda": 0.0}
    options = [-2.0, -1.0, 0.0, 1.0, 2.0]

    with pytest.raises(AdaptiveSamplingDisabledError) as exc_info:
        generate(
            n_trials=N_TRIALS,
            options=options,
            params=params,
            n_blocks=1,
            sampling_method="boed",
        )
    assert "PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING" in str(exc_info.value)


def test_boed_sampling_works_when_flag_enabled():
    """BOED sampling works when feature flag is enabled."""
    os.environ["PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING"] = "1"
    try:
        params = {"x_0": 0.0, "k": 1.0, "gamma": 0.0, "lambda": 0.0}
        options = [-2.0, -1.0, 0.0, 1.0, 2.0]

        result = generate(
            n_trials=N_TRIALS,
            options=options,
            params=params,
            n_blocks=1,
            sampling_method="boed",
            random_seed=42,
        )
        assert len(result) == N_TRIALS
        assert "Intensity" in result.columns
        assert "Result" in result.columns
    finally:
        os.environ.pop("PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING", None)


def test_constant_stimuli_works_regardless_of_flag():
    """Constant stimuli sampling works even when flag is disabled."""
    os.environ.pop("PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING", None)

    params = {"x_0": 0.0, "k": 1.0, "gamma": 0.0, "lambda": 0.0}
    options = [-2.0, -1.0, 0.0, 1.0, 2.0]

    result = generate(
        n_trials=N_TRIALS,
        options=options,
        params=params,
        n_blocks=1,
        sampling_method="constant_stimuli",
        random_seed=42,
    )
    assert len(result) == N_TRIALS
