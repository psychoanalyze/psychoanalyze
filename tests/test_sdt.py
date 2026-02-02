"""Tests for Signal Detection Theory (SDT) analysis module."""

import numpy as np
import polars as pl
import pytest
from scipy import stats

from psychoanalyze.analysis import sdt


class TestDPrime:
    """Tests for d' (d-prime) calculation."""

    def test_equal_rates_gives_zero(self) -> None:
        """d' should be 0 when hit rate equals false alarm rate (chance performance)."""
        assert sdt.d_prime(0.5, 0.5) == pytest.approx(0.0, abs=1e-6)
        assert sdt.d_prime(0.3, 0.3) == pytest.approx(0.0, abs=1e-6)
        assert sdt.d_prime(0.8, 0.8) == pytest.approx(0.0, abs=1e-6)

    def test_perfect_discrimination(self) -> None:
        """d' should be large for perfect discrimination (HR=1, FAR=0)."""
        # With clipping to 0.999 and 0.001, we get a large but finite value
        result = sdt.d_prime(1.0, 0.0)
        assert result > 6.0  # Very large d'

    def test_known_values(self) -> None:
        """Test d' calculation against known values."""
        # When HR = 0.8 and FAR = 0.2
        # Z(0.8) ≈ 0.842, Z(0.2) ≈ -0.842
        # d' = 0.842 - (-0.842) ≈ 1.684
        assert sdt.d_prime(0.8, 0.2) == pytest.approx(1.684, abs=0.01)
        
        # When HR = 0.9 and FAR = 0.3
        # Z(0.9) ≈ 1.282, Z(0.3) ≈ -0.524
        # d' = 1.282 - (-0.524) ≈ 1.806
        assert sdt.d_prime(0.9, 0.3) == pytest.approx(1.806, abs=0.01)

    def test_higher_hr_increases_d_prime(self) -> None:
        """Higher hit rate with same FAR should increase d'."""
        d1 = sdt.d_prime(0.7, 0.2)
        d2 = sdt.d_prime(0.8, 0.2)
        d3 = sdt.d_prime(0.9, 0.2)
        assert d1 < d2 < d3

    def test_lower_far_increases_d_prime(self) -> None:
        """Lower false alarm rate with same HR should increase d'."""
        d1 = sdt.d_prime(0.8, 0.4)
        d2 = sdt.d_prime(0.8, 0.3)
        d3 = sdt.d_prime(0.8, 0.2)
        assert d1 < d2 < d3

    def test_boundary_clipping(self) -> None:
        """Extreme values should be clipped to avoid infinite d'."""
        # These would give inf/-inf without clipping
        result = sdt.d_prime(1.0, 0.0)
        assert np.isfinite(result)
        assert result > 0
        
        result = sdt.d_prime(0.0, 1.0)
        assert np.isfinite(result)
        assert result < 0


class TestCriterion:
    """Tests for criterion (c) calculation."""

    def test_unbiased_criterion(self) -> None:
        """Unbiased responding (equal Z-scores) should give c ≈ 0."""
        # When HR and FAR are symmetric around 0.5
        assert sdt.criterion(0.8, 0.2) == pytest.approx(0.0, abs=0.01)
        assert sdt.criterion(0.7, 0.3) == pytest.approx(0.0, abs=0.01)

    def test_liberal_bias(self) -> None:
        """High HR and high FAR indicates liberal bias (c < 0)."""
        c = sdt.criterion(0.9, 0.7)
        assert c < 0

    def test_conservative_bias(self) -> None:
        """Low HR and low FAR indicates conservative bias (c > 0)."""
        c = sdt.criterion(0.3, 0.1)
        assert c > 0

    def test_known_values(self) -> None:
        """Test criterion calculation against known values."""
        # c = -0.5 * [Z(HR) + Z(FAR)]
        # When HR=0.9, FAR=0.7: Z(0.9)≈1.282, Z(0.7)≈0.524
        # c = -0.5 * (1.282 + 0.524) ≈ -0.903
        assert sdt.criterion(0.9, 0.7) == pytest.approx(-0.903, abs=0.01)


class TestBeta:
    """Tests for beta (likelihood ratio) calculation."""

    def test_unbiased_beta(self) -> None:
        """Unbiased responding should give beta ≈ 1."""
        assert sdt.beta(0.8, 0.2) == pytest.approx(1.0, abs=0.01)
        assert sdt.beta(0.7, 0.3) == pytest.approx(1.0, abs=0.01)

    def test_conservative_beta(self) -> None:
        """Conservative bias should give beta > 1."""
        b = sdt.beta(0.3, 0.1)
        assert b > 1.0

    def test_liberal_beta(self) -> None:
        """Liberal bias should give beta < 1."""
        b = sdt.beta(0.9, 0.7)
        assert b < 1.0


class TestComputeHRFAR:
    """Tests for computing hit rate and false alarm rate from trials."""

    def test_simple_split(self) -> None:
        """Test basic HR/FAR computation with clear signal/noise split."""
        trials = pl.DataFrame({
            "Intensity": [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0],
            "Result": [0, 0, 1, 1, 1, 1, 1, 0],  # FAR=0.5, HR=0.75
        })
        
        rates = sdt.compute_hr_far(trials, criterion=0.5)
        
        assert rates["hit_rate"] == 0.75  # 3/4 hits at high intensity
        assert rates["false_alarm_rate"] == 0.5  # 2/4 false alarms at low
        assert rates["n_signal_trials"] == 4
        assert rates["n_noise_trials"] == 4

    def test_all_noise_trials_error(self) -> None:
        """Should raise error if criterion puts all trials on one side."""
        trials = pl.DataFrame({
            "Intensity": [1.0, 1.0, 1.0, 1.0],
            "Result": [1, 1, 0, 1],
        })
        
        with pytest.raises(ValueError, match="need trials both above and below"):
            sdt.compute_hr_far(trials, criterion=0.0)  # All above criterion

    def test_custom_column_names(self) -> None:
        """Should work with custom column names."""
        trials = pl.DataFrame({
            "stim_level": [0.0, 0.0, 1.0, 1.0],
            "response": [0, 1, 1, 1],
        })
        
        rates = sdt.compute_hr_far(
            trials, 
            criterion=0.5,
            intensity_col="stim_level",
            result_col="response",
        )
        
        assert rates["hit_rate"] == 1.0
        assert rates["false_alarm_rate"] == 0.5


class TestSDTFromTrials:
    """Tests for computing all SDT metrics from trial data."""

    def test_complete_metrics(self) -> None:
        """Should return all expected SDT metrics."""
        trials = pl.DataFrame({
            "Intensity": [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0],
            "Result": [0, 0, 1, 0, 1, 1, 1, 0],  # FAR=0.25, HR=0.75
        })
        
        metrics = sdt.sdt_from_trials(trials, criterion_threshold=0.5)
        
        # Check all expected keys are present
        expected_keys = {
            "hit_rate", "false_alarm_rate",
            "n_signal_trials", "n_noise_trials",
            "d_prime", "criterion_c", "beta",
        }
        assert set(metrics.keys()) == expected_keys
        
        # Check values are sensible
        assert 0 <= metrics["hit_rate"] <= 1
        assert 0 <= metrics["false_alarm_rate"] <= 1
        assert metrics["d_prime"] > 0  # Should have positive sensitivity
        assert np.isfinite(metrics["criterion_c"])
        assert metrics["beta"] > 0

    def test_high_sensitivity_data(self) -> None:
        """Should detect high d' when discrimination is good."""
        # Perfect discrimination
        trials = pl.DataFrame({
            "Intensity": [0.0] * 10 + [1.0] * 10,
            "Result": [0] * 10 + [1] * 10,
        })
        
        metrics = sdt.sdt_from_trials(trials, criterion_threshold=0.5)
        
        assert metrics["hit_rate"] == 1.0
        assert metrics["false_alarm_rate"] == 0.0
        assert metrics["d_prime"] > 6.0  # Very high sensitivity


class TestSDTFromParams:
    """Tests for extracting SDT metrics from psychometric parameters."""

    def test_extracts_all_fields(self) -> None:
        """Should extract all expected SDT-related fields."""
        params = {
            "x_0": 0.0,
            "k": 1.5,
            "gamma": 0.1,
            "lambda": 0.05,
        }
        
        sdt_metrics = sdt.sdt_from_params(params)
        
        expected_keys = {
            "d_prime_approx", "threshold", "far_approx",
            "lapse_rate", "sensitivity_range",
        }
        assert set(sdt_metrics.keys()) == expected_keys

    def test_slope_maps_to_d_prime(self) -> None:
        """Slope k should map to approximate d'."""
        params = {"x_0": 0.0, "k": 2.0, "gamma": 0.0, "lambda": 0.0}
        result = sdt.sdt_from_params(params)
        assert result["d_prime_approx"] == 2.0

    def test_gamma_maps_to_far(self) -> None:
        """Gamma (guess rate) should map to approximate FAR."""
        params = {"x_0": 0.0, "k": 1.0, "gamma": 0.15, "lambda": 0.0}
        result = sdt.sdt_from_params(params)
        assert result["far_approx"] == 0.15

    def test_sensitivity_range(self) -> None:
        """Sensitivity range should be 1 - gamma - lambda."""
        params = {"x_0": 0.0, "k": 1.0, "gamma": 0.1, "lambda": 0.05}
        result = sdt.sdt_from_params(params)
        assert result["sensitivity_range"] == pytest.approx(0.85)


class TestROCCurve:
    """Tests for ROC curve generation."""

    def test_returns_dataframe(self) -> None:
        """Should return a polars DataFrame with expected columns."""
        trials = pl.DataFrame({
            "Intensity": np.linspace(-2, 2, 100),
            "Result": np.random.binomial(1, 0.5, 100),
        })
        
        roc = sdt.roc_curve(trials, n_points=10)
        
        assert isinstance(roc, pl.DataFrame)
        assert set(roc.columns) == {"criterion", "hit_rate", "false_alarm_rate", "d_prime"}
        assert len(roc) > 0  # Should have some valid points

    def test_hit_rate_decreases_with_criterion(self) -> None:
        """Hit rate should generally decrease as criterion increases."""
        # Create data with clear signal: high intensity → high response rate
        np.random.seed(42)
        intensities = np.linspace(-2, 2, 200)
        probs = 1 / (1 + np.exp(-2 * intensities))  # Logistic function
        results = (np.random.random(200) < probs).astype(int)
        
        trials = pl.DataFrame({
            "Intensity": intensities,
            "Result": results,
        })
        
        roc = sdt.roc_curve(trials, n_points=15)
        
        # Sort by criterion
        roc = roc.sort("criterion")
        
        # Hit rate should generally decrease as criterion increases
        # (though not strictly monotonic due to sampling)
        hit_rates = roc["hit_rate"].to_numpy()
        # Check that at least the endpoints follow expected pattern
        assert hit_rates[0] > hit_rates[-1]

    def test_custom_column_names(self) -> None:
        """Should work with custom column names."""
        trials = pl.DataFrame({
            "stim": np.linspace(0, 1, 50),
            "resp": np.random.binomial(1, 0.5, 50),
        })
        
        roc = sdt.roc_curve(
            trials, 
            n_points=5,
            intensity_col="stim",
            result_col="resp",
        )
        
        assert len(roc) > 0


class TestAUC:
    """Tests for Area Under the ROC Curve calculation."""

    def test_perfect_discrimination(self) -> None:
        """Perfect ROC (HR=1, FAR=0) should give AUC=1.0."""
        hrs = [0.0, 1.0, 1.0]
        fars = [0.0, 0.0, 1.0]
        
        result = sdt.auc(hrs, fars)
        assert result == pytest.approx(1.0, abs=0.01)

    def test_chance_performance(self) -> None:
        """Diagonal ROC (HR=FAR) should give AUC=0.5."""
        hrs = [0.0, 0.5, 1.0]
        fars = [0.0, 0.5, 1.0]
        
        result = sdt.auc(hrs, fars)
        assert result == pytest.approx(0.5, abs=0.01)

    def test_intermediate_performance(self) -> None:
        """Intermediate ROC should give 0.5 < AUC < 1.0."""
        hrs = [0.0, 0.5, 0.8, 1.0]
        fars = [0.0, 0.1, 0.3, 1.0]
        
        result = sdt.auc(hrs, fars)
        assert 0.5 < result < 1.0

    def test_unsorted_input(self) -> None:
        """Should handle unsorted input by sorting automatically."""
        # Provide points in random order
        hrs = [0.8, 1.0, 0.0, 0.5]
        fars = [0.3, 1.0, 0.0, 0.1]
        
        result = sdt.auc(hrs, fars)
        assert np.isfinite(result)
        assert 0 <= result <= 1


class TestAUCFromROC:
    """Tests for computing AUC from ROC DataFrame."""

    def test_integration_with_roc_curve(self) -> None:
        """Should integrate with roc_curve() output."""
        # Create data with known good discrimination
        np.random.seed(42)
        intensities = np.linspace(-2, 2, 200)
        probs = 1 / (1 + np.exp(-3 * intensities))  # Strong logistic
        results = (np.random.random(200) < probs).astype(int)
        
        trials = pl.DataFrame({
            "Intensity": intensities,
            "Result": results,
        })
        
        roc = sdt.roc_curve(trials, n_points=20)
        auc_value = sdt.auc_from_roc(roc)
        
        # Should have good discrimination
        assert auc_value > 0.8
        assert auc_value <= 1.0

    def test_chance_data(self) -> None:
        """Random data should give AUC near 0.5."""
        np.random.seed(123)
        trials = pl.DataFrame({
            "Intensity": np.random.random(100),
            "Result": np.random.binomial(1, 0.5, 100),
        })
        
        roc = sdt.roc_curve(trials, n_points=15)
        auc_value = sdt.auc_from_roc(roc)
        
        # Should be near chance (within reasonable error for random data)
        assert 0.3 < auc_value < 0.7
