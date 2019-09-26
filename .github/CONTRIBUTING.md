# How To Contribute

Thanks for taking the time to contribute to our package!

## Guidelines

* Try to limit PRs to 1 change per pull request.
* Please fill out the pull pull request template with relevant context.
* Changes will only be accepted if [CI](https://travis-ci.com/klaviyo/matrix_enum)
is passing. If you think CI is failing incorrectly, please mention this in your PR.


## Running Tests

Tests, linting, and code coverage checks are all run with CI when a Pull
Request is made.

Before making a PR, you can run tests locally by performing the following:

```bash
# Install development dependencies
$ pip install .[dev]
# Run the test suite in all supported python versions
$ tox
```

This will run all the same tests and checks as our CI. On failures, you can
you can use the verbosity `-v` flags with `tox` to get more information.a

### Local testing FAQ

#### Different shells
If you're using a non-`bash` shell (eg `zsh`), you may have to escape your `[`s:

```bash
$ pip install .\[dev\]
```

#### Python Versions

`tox` does **not** handle installing multiple versions of python. If you're missing
a version `tox` will skip that version and you'll see a skipped note.

```bash
SKIPPED: InterpreterNotFound: python3.4
```

If you want to test with any skipped versions, you'll have to install the missing
versions of python.

An example of how to do this would be to use [pyenv](https://github.com/pyenv/pyenv)
to install and manage multiple versions

For example:

```bash
# Install the version
$ pyenv install 3.4.10
# Make the version available to your local directory
$ pyenv local 3.4.10
# Run tox with this version available
$ tox
```
