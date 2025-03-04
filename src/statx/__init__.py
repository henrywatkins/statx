"""Statx - statsmodels on the command line"""

__version__ = "0.1.0"

# Make key components available at package level
from statx.cli import statx
from statx.stats import run_ols, run_logit, run_ttest, run_anova, run_glm

__all__ = ["statx", "run_ols", "run_logit", "run_ttest", "run_anova", "run_glm"]
