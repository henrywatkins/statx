import click
import statx
import sys

import click
import pandas as pd
from io import StringIO
from typing import Dict, List, Tuple, Any, Callable, Optional

# Example version; in a real package you might import this from an __about__ module.
__version__ = "0.1.0"


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="statx")
@click.argument("input_file", type=click.File("r"), default="-")
@click.option(
    "--program",
    "-p",
    type=str,
    required=True,
    help="Script string, the parameters for the statistical test",
)
@click.option(
    "--output",
    "-o",
    type=str,
    help="File where you would like to save the test output",
)
@click.option(
    "--file",
    "-f",
    type=click.File("r"),
    help="Script file. Instead of using a string, you can define the test parameters in a file",
)
@click.option(
    "--separator",
    "-s",
    type=str,
    default=",",
    help="Separator for input data, default is ','",
)
@click.option(
    "--columns",
    "-c",
    type=str,
    default=None,
    help="Column names for the input data, if not present in the file",
)
def statx(
    program: str,
    columns: Optional[str],
    input_file,
    output: Optional[str],
    file,
    separator: str,
) -> int:
    """
    Terminal-based statistical testing with statsmodels

    Perform statistical tests on tabular data (CSV or stdin) directly from the terminal.
    Supported tests:
      * ols: Ordinary Least Squares Regression. Required parameters: dependent, independent.
      * logit: Logistic Regression. Required parameters: dependent, independent.
      * ttest: Two-sample t-test. Required parameters: sample1, sample2. Optional: alternative (two-sided, larger, smaller).
      * anova: ANOVA test. Required parameter: formula (e.g., "y ~ C(x)").

    Define the test parameters using a script string. For example:

        statx data.csv -p "test:ols,dependent:y,independent:x+z"

    If no column names are provided via --columns, the first line of the file is assumed to be the header.
    """
    if file:
        program = file.read()

    try:
        test_func, test_args = parse_script(program)
    except Exception as e:
        click.echo(f"Error: Invalid script format: {str(e)}")
        return 1

    try:
        column_names = parse_columns(columns)
        contents = input_file.read()
        name_dict = {"names": column_names} if column_names else {}
        df = pd.read_csv(StringIO(contents), sep=separator, **name_dict)

        result = test_func(df, **test_args)

        if output:
            with open(output, "w") as f:
                f.write(result)
            click.echo(f"Test result saved to {output}")
        else:
            click.echo(result)
        return 0
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return 1


def parse_columns(column_string: Optional[str]) -> List[str]:
    """Parse comma-separated column names into a list.

    Args:
        column_string: A comma-separated string of column names

    Returns:
        A list of column names.
    """
    if column_string:
        return [col.strip() for col in column_string.strip().split(",")]
    else:
        return []


def parse_script(script_string: str) -> Tuple[Callable, Dict[str, Any]]:
    """
    Parse the script string and return the test function and its arguments.

    The script string should be formatted as key:value pairs separated by commas.
    Example:
        "test:ols,dependent:y,independent:x+z"
    """
    if not script_string or not script_string.strip():
        raise ValueError("Empty script string")

    elements = script_string.strip()
    try:
        # Use split with maxsplit=1 for values in case they contain colons.
        elements_dict = dict(
            (item.split(":", 1)[0].strip(), item.split(":", 1)[1].strip())
            for item in elements.split(",")
        )
    except IndexError:
        raise ValueError(
            "Invalid format. Expected 'key:value' pairs separated by commas"
        )

    test_types = {
        "ols": run_ols,
        "logit": run_logit,
        "ttest": run_ttest,
        "anova": run_anova,
    }

    # Default to "ols" if no test key is provided.
    if "test" not in elements_dict:
        test_choice = "ols"
    elif elements_dict["test"] in test_types:
        test_choice = elements_dict["test"]
    else:
        raise ValueError(
            f"Invalid test type. Supported tests: {', '.join(test_types.keys())}"
        )

    # Remove the test key from parameters.
    elements_dict.pop("test", None)

    # Verify required parameters for each test.
    if test_choice in ["ols", "logit"]:
        if "dependent" not in elements_dict or "independent" not in elements_dict:
            raise ValueError(
                f"{test_choice} requires 'dependent' and 'independent' parameters"
            )
    elif test_choice == "ttest":
        if "sample1" not in elements_dict or "sample2" not in elements_dict:
            raise ValueError("ttest requires 'sample1' and 'sample2' parameters")
    elif test_choice == "anova":
        if "formula" not in elements_dict:
            raise ValueError("anova requires 'formula' parameter")

    return test_types[test_choice], elements_dict


def run_ols(data: pd.DataFrame, dependent: str, independent: str, **kwargs) -> str:
    """Run an Ordinary Least Squares regression test using statsmodels."""
    import statsmodels.formula.api as smf

    formula = f"{dependent} ~ {independent}"
    model = smf.ols(formula, data=data).fit()
    return model.summary().as_text()


def run_logit(data: pd.DataFrame, dependent: str, independent: str, **kwargs) -> str:
    """Run a logistic regression test using statsmodels."""
    import statsmodels.formula.api as smf

    formula = f"{dependent} ~ {independent}"
    # disp=False suppresses convergence output
    model = smf.logit(formula, data=data).fit(disp=False)
    return model.summary().as_text()


def run_ttest(data: pd.DataFrame, sample1: str, sample2: str, **kwargs) -> str:
    """Run a two-sample t-test using statsmodels."""
    from statsmodels.stats.weightstats import ttest_ind

    s1 = data[sample1].dropna()
    s2 = data[sample2].dropna()
    alternative = kwargs.get("alternative", "two-sided")
    tstat, pvalue, df = ttest_ind(s1, s2, alternative=alternative)
    return f"t-statistic: {tstat}\np-value: {pvalue}\ndegrees of freedom: {df}"


def run_anova(data: pd.DataFrame, formula: str, **kwargs) -> str:
    """Run an ANOVA test using statsmodels."""
    from statsmodels.formula.api import ols
    import statsmodels.api as sm

    model = ols(formula, data=data).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    return anova_table.to_string()
