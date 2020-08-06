[![MatrixEnum Logo](https://raw.githubusercontent.com/klaviyo/matrix_enum/master/img/logo.jpg)](https://github.com/klaviyo/matrix_enum)

# `MatrixEnum`

[![Build Status](https://travis-ci.com/klaviyo/matrix_enum.svg?token=oiB5ARPJxDf7ncG5fL9x&branch=master)](https://travis-ci.com/klaviyo/matrix_enum)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/matrix_enum)

`MatrixEnum` is a package that provides convenient extensions to python's
builtin enums to allow for simple construction of enum multi-dimensional members.

```python
from matrix_enum import MatrixEnum, Member

class MyEnum(MatrixEnum):
    ONE = Member(digit=1, title='one', roman='I')
    TWO = Member(digit=2, title='two', roman='II')

# Keeps classic enum functionality
>>> MyEnum.ONE is MyEnum.TWO
False
>>> MyEnum.ONE is MyEnum.ONE
True

# Automatically adds attributes to all enum members
>>> MyEnum.ONE.digit
1
>>> MyEnum.ONE.title
'one'

# `Member` attributes are reversible
>>> MyEnum.ONE is MyEnum(1)
True
>>> MyEnum.TWO is MyEnum('II')
True
>>> 1 in MyEnum
True
>>> 'two' in MyEnum
True
```

## Installation

You can either install the package with pip:

```bash
$ pip install matrix_enum
```

or clone the repo and install:


```bash
$ git clone https://github.com/klaviyo/matrix_enum.git
$ pip install -e matrix_enum/
```

## Local Development

For information on local development, testing, and contributing, see the
[Contribution guidelines for this project](docs/CONTRIBUTING.md).

---

## API

### `MatrixEnum` and `Members`

`MatrixEnum` extends the basic python `Enum` with the following restrictions:
* All members must be of type `Member`.
* All `Member`s must have the same attributes.
* All values of `Member` attributes must be unique across ALL attributes.
* `Member` attributes cannot use any reserved `__dunder__` attributes or the
names `name` or `value`.

#### Valid

The following is a valid `MatrixEnum`:
```python
from matrix_enum import MatrixEnum, Member

class MyEnum(MatrixEnum):
    ONE = Member(digit=1, title='one', roman='I')
    TWO = Member(digit=2, title='two', roman='II')
```


#### Invalid Enums

All of the following are ***INVALID*** `MatrixEnums` and will raise a
`ValueError`:

```python
# INVALID: The members have to be of class Member
class NonMembers(MatrixEnum):
    ONE = 1
    TWO = 2

# INVALID: Members have the same value for 'digit'
class DuplicateValue(MatrixEnum):
    ONE = Member(digit=1)
    OTHER_ONE = Member(digit=1)

# INVALID: Members can't have the same value across different attributes
class DuplicateValue2(MatrixEnum):
    FOO = Member(digit=1, other_digit=2)
    BAR = Member(digit=3, other_digit=1)

# INVALID: Members have different attributes
class UnevenAttrs(MatrixEnum):
    ONE = Member(digit=1, title='one')
    TWO = Member(digit=2, roman='II')
```

### Adding `extra`s

You can add duplicated values to `Member`s using the `extra` method.

These `extra`s will be available as attributes to members but cannot be used
to lookup enum members by value.


```python
class AnimalEnum(MatrixEnum):
    CAT = Member(title='cat').extra(num_paws=4)
    DOG = Member(title='dog').extra(num_paws=4)
    FISH = Member(title='fish').extra(num_paws=0)

>>> AnimalEnum.CAT.num_paws
4
>>> AnimalEnum(4)
ValueError: 4 is not a valid AnimalEnum
```


### Links

* Code: https://github.com/klaviyo/matrix_enum
* Release: https://pypi.org/project/matrix_enum/
* Changelog: https://github.com/klaviyo/matrix_enum/blob/master/CHANGELOG.md

---

This package is owned and maintained by [Klaviyo](https://www.klaviyo.com). Check out our [eng blog](https://klaviyo.tech/).
