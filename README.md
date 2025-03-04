# statx

Statsmodels on the command line - a powerful CLI for running statistical tests directly in your terminal.

## Installation

```bash
pip install statx
```

If you're using Rye:
```bash
rye add statx
```

## Features

- **Simple CLI interface**: Run statistical tests without writing Python code
- **Multiple test types**: OLS, Logistic Regression, t-tests, ANOVA
- **Input flexibility**: Works with CSV files or piped stdin data
- **Integration with Unix tools**: Pairs perfectly with awk, grep, sed, jq, etc.

## Usage

```bash
# Basic syntax
statx [INPUT_FILE] -p "test:TYPE,PARAM1:VALUE1,PARAM2:VALUE2"

# Example: OLS regression on data.csv
statx data.csv -p "test:ols,dependent:y,independent:x+z"

# Read from stdin
cat data.csv | statx -p "test:ttest,sample1:group1,sample2:group2"
```

## Supported Tests

### Ordinary Least Squares (OLS) Regression

```bash
statx data.csv -p "test:ols,dependent:y,independent:x+z+w"
```

Required parameters:
- `dependent`: The dependent variable column
- `independent`: Formula for independent variables (e.g., `x+z+w` or `x*z`)

### Logistic Regression

```bash
statx data.csv -p "test:logit,dependent:binary_outcome,independent:x+z"
```

Required parameters:
- `dependent`: The binary dependent variable column
- `independent`: Formula for independent variables

### Generalized Linear Models (GLM)

```bash
statx data.csv -p "test:glm,dependent:y,independent:x+z,family:poisson,link:log"
```

Required parameters:
- `dependent`: The dependent variable column
- `independent`: Formula for independent variables
- `family`: Distribution family - one of:
  - `gaussian`: For continuous data (normal distribution)
  - `binomial`: For binary data (0/1)
  - `poisson`: For count data
  - `gamma`: For positive continuous data with variance proportional to square of mean
  - `inverse_gaussian`: For positive continuous data
  - `neg_binomial`: For overdispersed count data
  - `tweedie`: For compound Poisson-gamma distribution

Optional parameters:
- `link`: Link function - depends on the family, common options include:
  - `identity`: No transformation (default for Gaussian)
  - `log`: Log transformation (default for Poisson and Gamma)
  - `logit`: Logit transformation (default for Binomial)
  - `probit`: Probit transformation
  - `cloglog`: Complementary log-log transformation
  - `inverse`: Inverse transformation
  - `power`: Power transformation
- `alpha`: Alpha parameter for NegativeBinomial family (default 1.0)
- `var_power`: Variance power for Tweedie family (default 1.5)
- `power`: Power parameter for Power link function (default 1.0)

Examples:
```bash
# Poisson regression with log link
statx data.csv -p "test:glm,dependent:count,independent:x+z,family:poisson"

# Gamma regression with log link
statx data.csv -p "test:glm,dependent:duration,independent:x+z,family:gamma"

# Binomial regression with probit link
statx data.csv -p "test:glm,dependent:success,independent:x+z,family:binomial,link:probit"
```

### Two-sample t-test

```bash
statx data.csv -p "test:ttest,sample1:group1,sample2:group2,alternative:two-sided"
```

Required parameters:
- `sample1`: First sample column name
- `sample2`: Second sample column name

Optional parameters:
- `alternative`: Test type ('two-sided', 'larger', or 'smaller')

### ANOVA

```bash
statx data.csv -p "test:anova,formula:y ~ C(group)"
```

Required parameters:
- `formula`: Statistical formula using patsy/statsmodels syntax

## Options

```
Options:
  --version             Show the version and exit.
  -p, --program TEXT    Script string, the parameters for the statistical test [required]
  -o, --output TEXT     File where you would like to save the test output
  -f, --file FILENAME   Script file. Instead of using a string, you can define the test parameters in a file
  -s, --separator TEXT  Separator for input data, default is ','
  -c, --columns TEXT    Column names for the input data, if not present in the file
  -h, --help            Show this message and exit.
```

## Examples

### CSV with headers

```bash
$ cat data.csv
x,y,group
1,3.4,A
2,5.7,A
3,6.3,B
4,8.1,B

$ statx data.csv -p "test:ols,dependent:y,independent:x"
```

### CSV without headers

```bash
$ cat data_no_header.csv
1,3.4,A
2,5.7,A
3,6.3,B
4,8.1,B

$ statx data_no_header.csv -p "test:ols,dependent:y,independent:x" -c "x,y,group"
```

### Saving output to file

```bash
$ statx data.csv -p "test:ols,dependent:y,independent:x" -o results.txt
```

## Development

See the [contributing guidelines](CONTRIBUTING.md) for information on reporting issues, feature requests, and development setup.

## License

[MIT License](LICENSE)
