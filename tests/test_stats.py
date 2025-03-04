"""Tests for the statistical functions."""

import pytest
from statx.cli import run_ols, run_logit, run_ttest, run_anova


def test_run_ols(sample_data):
    """Test the OLS regression function."""
    result = run_ols(sample_data, dependent="y", independent="x")
    assert "OLS Regression Results" in result
    assert "R-squared:" in result
    assert "Prob (F-statistic):" in result


def test_run_logit(sample_data):
    """Test the logistic regression function."""
    # Convert y to binary for logit test
    data = sample_data.copy()
    data["binary"] = (data["y"] > data["y"].median()).astype(int)

    result = run_logit(data, dependent="binary", independent="x")
    assert "Logit Regression Results" in result
    assert "Pseudo R-squared:" in result
    assert "Log-Likelihood:" in result


def test_run_ttest(sample_data):
    """Test the t-test function."""
    result = run_ttest(sample_data, sample1="x", sample2="y", alternative="two-sided")
    assert "t-statistic:" in result
    assert "p-value:" in result
    assert "degrees of freedom:" in result

    # Test with different alternative
    result = run_ttest(sample_data, sample1="x", sample2="y", alternative="larger")
    assert "t-statistic:" in result
    assert "p-value:" in result


def test_run_anova(sample_data):
    """Test the ANOVA function."""
    result = run_anova(sample_data, formula="y ~ C(group)")
    assert "sum_sq" in result
    assert "df" in result
    assert "F" in result
    assert "PR(>F)" in result
