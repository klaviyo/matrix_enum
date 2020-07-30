from __future__ import unicode_literals

import sys
from unittest import TestCase

import pytest

from matrix_enum import MatrixEnum, Member


class TestWorkingEnums(TestCase):
    def test_member_hashing(self):
        assert hash(Member(foo=1)) != hash(Member(bar=1))

    def test_simple_enum(self):
        class WorkingEnum(MatrixEnum):
            ONE = Member(code=1, description='one', plain_text='plaintext')
            TWO = Member(code=2, description='two', plain_text='something else plain')

        assert isinstance(WorkingEnum.ONE, WorkingEnum)

        assert WorkingEnum.ONE is WorkingEnum['ONE']
        assert WorkingEnum(1) is WorkingEnum.ONE
        assert WorkingEnum(1) == WorkingEnum.ONE
        assert WorkingEnum('one') is WorkingEnum('plaintext')
        assert WorkingEnum.ONE.value != Member(code=1)
        assert WorkingEnum.ONE.description == 'one'
        assert WorkingEnum.ONE.plain_text == 'plaintext'
        assert WorkingEnum.ONE.code == 1
        assert WorkingEnum.ONE.code == WorkingEnum.ONE.value.code
        assert WorkingEnum.ONE != WorkingEnum.TWO
        assert WorkingEnum.ONE.value != WorkingEnum.TWO.value
        assert WorkingEnum(1) != WorkingEnum(2)
        assert WorkingEnum('one') != WorkingEnum('two')
        assert WorkingEnum['ONE'] != WorkingEnum['TWO']

        identical_member = Member(code=1, description='one', plain_text="plaintext")
        assert WorkingEnum.ONE.value == identical_member
        assert WorkingEnum.ONE.value is not identical_member
        for item in WorkingEnum:
            assert item in WorkingEnum

        # TODO: Port and test or kill?
        # assert fully_qualified_name(WorkingEnum.ONE) == 'tests.test_enums.WorkingEnum'

    def test_additional_functions(self):
        class WorkingEnum(MatrixEnum):
            ONE = Member(code=1)
            TWO = Member(code=2)

            def code_label(self):
                return "My code is {}".format(self.code)

            @classmethod
            def total_codes(cls):
                return sum(e.code for e in cls)

        self.assertEqual(WorkingEnum.ONE.code_label(), "My code is 1")
        self.assertEqual(WorkingEnum.total_codes(), 3)

    def test_contains(self):
        class MyEnum(MatrixEnum):
            ONE = Member(code=1, description='one').extra(foo='bar')
            TWO = Member(code=2, description='two').extra(foo='baz')

            @classmethod
            def test_func(cls):
                return "Test"

        assert 1 in MyEnum
        assert 2 in MyEnum
        assert 3 not in MyEnum
        assert 'one' in MyEnum
        assert 'two' in MyEnum
        assert 'three' not in MyEnum
        assert MyEnum.ONE in MyEnum
        assert MyEnum.TWO in MyEnum
        # Extras cannot be verified with `in`
        assert 'bar' not in MyEnum
        assert 'baz' not in MyEnum
        # Enum methods should not be `in` the enum
        assert MyEnum.test_func not in MyEnum

    def test_none_values(self):
        class MyEnum(MatrixEnum):
            ONE = Member(code=1)
            NONE = Member(code=None)

        assert None in MyEnum
        assert MyEnum(None) is MyEnum.NONE

    def test_full_name(self):
        class MyEnum(MatrixEnum):
            ONE = Member(code=1)
            TWO = Member(code=2)

        test_member = MyEnum.ONE
        full_name = test_member.__class__.__module__ + '.' + test_member.__class__.__name__
        assert full_name == 'tests.test_enum.MyEnum'


class TestBrokenEnums(TestCase):
    def test_ambiguous_member(self):
        with pytest.raises(ValueError, match=r"Ambiguous Member: one"):
            class BadEnum(MatrixEnum):
                ONE = Member(code=1, description='one', plain_text="plaintext")
                TWO = Member(code=2, description='one', plain_text="something else plain")

    def test_different_member_attrs(self):
        with pytest.raises(ValueError, match=r"Members have different addressable keys; \['bar'\] vs\. \['foo'\]"):
            class BadEnum(MatrixEnum):
                ONE = Member(foo=1)
                TWO = Member(bar=2)

    def test_non_members(self):
        with pytest.raises(ValueError, match=r"\(3, u?'three'\) is not a Member"):
            class BadEnum(MatrixEnum):
                ONE = Member(code=1, description='one')
                TWO = Member(code=2, description='two')
                THREE = (3, "three")

        with pytest.raises(ValueError, match=r"1 is not a Member"):
            class BadEnum1(MatrixEnum):
                ONE = 1
                TWO = 1

    def test_invalid_attrs(self):
        with pytest.raises(ValueError, match=r"'value' is not allowed as a key."):
            class BadEnum(MatrixEnum):
                ONE = Member(value=1, description='one', plain_text="plaintext")
                TWO = Member(value=2, description='one', plain_text="something else plain")

        with pytest.raises(ValueError, match=r"'name' is not allowed as a key."):
            class BadEnum1(MatrixEnum):
                ONE = Member(name=1, description='one', plain_text="plaintext")
                TWO = Member(name=2, description='one', plain_text="something else plain")

    def test_invalid_enums(self):
        with pytest.raises(ValueError, match=r"Key code is not allowed."):
            class BadEnum(MatrixEnum):
                ONE = Member(code=1)
                code = Member(code=2)

        with pytest.raises(ValueError, match=r"Key _reversed is not allowed."):
            class BadEnum1(MatrixEnum):
                _reversed = Member(code=1)
                _other = Member(code=2)


class TestBrokenMembers(TestCase):
    def test_duplicated_attr_values(self):
        with pytest.raises(ValueError, match=r"Value '1' duplicated within Member specification."):
            Member(code=1, description='one', plain_text=1)

    def test_invalid_attrs(self):
        with pytest.raises(ValueError, match=r"Member attribute 'extra' is not allowed."):
            Member(extra=6)  # 'extra' is a function on Member and cannot be used


class TestExtras(TestCase):
    def test_missing_extra(self):
        with pytest.raises(ValueError, match=r"Members have different extra keys; \['bar', 'foo'\] vs. \['foo'\]"):
            class BadEnum(MatrixEnum):
                ONE = Member(code=1, description='one', plain_text='plaintext').extra(foo=1)
                TWO = Member(code=2, description='two', plain_text='something else plain').extra(foo=2, bar=2)

    def test_extra_extras(self):
        with pytest.raises(ValueError, match=r"Can't set extras twice\."):
            class BadEnum(MatrixEnum):
                ONE = Member(code=1).extra(foo=1).extra(bar=3)
                TWO = Member(code=2).extra(foo=2).extra(bar=3)

    def test_valid_extra(self):
        class WorkingEnum(MatrixEnum):
            ONE = Member(code=1, description='one', plain_text='plaintext').extra(foo='1')
            TWO = Member(code=2, description='two', plain_text='something else plain').extra(foo='2')
            THREE = Member(code=3, description='three', plain_text='even more plain').extra(foo='1')

        assert WorkingEnum.TWO.foo == '2'
        # Slightly different printing in 2 backport vs 3
        with pytest.raises(ValueError, match=r"'?1'? is not a valid WorkingEnum"):
            # Extra should not be reversible like regular member attrs
            assert WorkingEnum('1') == WorkingEnum.ONE


class TestSunderAttrs(TestCase):
    # Explicitly test sunder attributes described in https://docs.python.org/3/library/enum.html#supported-sunder-names
    # We already handle callables, so only check static attributes

    def setUp(self):
        py_version_info = sys.version_info
        # Change once we drop 2 to: self.py_major, self.py_minor, *_ = sys.version_info
        self.py_major = py_version_info[0]
        self.py_minor = py_version_info[1]

    def test_order(self):
        # Order needs to remain respected
        class Enum(MatrixEnum):
            _order_ = 'TWO ONE'
            TWO = Member(code=2)
            ONE = Member(code=1)
        assert [m.code for m in Enum] == [2, 1]

        if self.py_major >= 3:
            # 3 + Will raise on an order mismatch
            with pytest.raises(TypeError, match=r"member order does not match _order_"):
                class Enum(MatrixEnum):
                    _order_ = 'TWO ONE'
                    ONE = Member(code=1)
                    TWO = Member(code=2)

    def test_ignore(self):
        try:
            class IgnoredEnum(MatrixEnum):
                _ignore_ = 'IGNORE_ME'
                ONE = Member(code=1)
                TWO = Member(code=2)
                IGNORE_ME = Member(code=3)
        except ValueError as e:
            if self.py_major >= 3 and self.py_minor >= 7:
                # Ignore only supported in 3.7+
                assert False, '_ignore_ should be supported in py 3.7+'
            else:
                # Otherwise we'll raise on adding a sunder
                assert '_names_ are reserved for future Enum use' in str(e)
        else:
            # 3 should not be included
            assert [m.code for m in IgnoredEnum] == [1, 2]
