from __future__ import unicode_literals

from enum import Enum, EnumMeta

from six import iteritems, with_metaclass

__all__ = ["MatrixEnum", "Member"]

_default_extra = dict()
_default_set = set()


class Member(object):
    """Namedtuple-esque entry for use in a MatrixEnum.

    Takes a list of kwargs (and only kwargs). No two kwargs may be duplicated,
    regardless of their key.

    All supplied kwargs are "keys" to a MatrixEnum which contains a given Member:
    since the enum enforces that all contained Members have the same keys and
    totally different values, any kwarg value passed to the constructor
    of any Member of a given MatrixEnum can be used to access that enum instance.

    All kwargs will become attributes of the Member, just like a namedtuple.

    Additional data that is *not* unique across all Members in an enum can be
    added to each member via the extra function, though data added that way
    cannot be used to look up Members in an enum.
    """

    def _dedupe_set(self, kwargs, unique=True):
        """Ensure member construction kwargs are valid."""
        values = set()
        for key, value in iteritems(kwargs):
            if key in ('value', 'name'):
                raise ValueError("'{}' is not allowed as a key.".format(key))
            elif unique and value in values:
                raise ValueError("Value '{}' duplicated within Member specification.".format(value))
            else:
                values.add(value)
                if hasattr(self, key):
                    raise ValueError("Member attribute '{}' is not allowed.".format(key))
                else:
                    setattr(self, key, value)

    def __init__(self, **kwargs):
        self._dedupe_set(kwargs)
        self._addressable = kwargs
        self._extra_homomorphic = _default_extra

    def __hash__(self):
        return hash(frozenset(self._addressable.keys()))

    def __eq__(self, other):
        return (
            type(other) is type(self)
            and self._addressable == other._addressable
            and self._extra_homomorphic == other._extra_homomorphic
        )

    def extra(self, **kwargs):
        """Set additional attributes on the member object.

        All keys must be novel (must not exist already in any form on the member).
        Values need not be unique. Different Members of the same MatrixEnum may
        *NOT* have different sets of keys for extra().

        This method can only be called once per Member.

        Returns: the Member instance, for convenient constructor chaining.
        """
        if self._extra_homomorphic is not _default_extra:
            raise ValueError('Can\'t set extras twice.')
        self._dedupe_set(kwargs, unique=False)
        self._extra_homomorphic = kwargs
        return self


class _MatrixEnumMeta(EnumMeta):
    """Metaclass to enforce unique Member constraints of MatrixEnum."""

    @staticmethod
    def _pgetter(key):
        return property(lambda self: getattr(self.value, key))

    def __new__(metacls, cls, bases, classdict):
        homomorphic_extras = _default_set
        allowed_keys = _default_set
        reversed_addressable = dict()
        for key, value in sorted(iteritems(classdict)):  # Sorted for consistent behavior across 2/3
            if isinstance(value, Member):
                # Check that all Members have the same addressable (main ctor) keys.
                if allowed_keys is _default_set:
                    allowed_keys = set(value._addressable.keys())
                elif set(value._addressable.keys()) != allowed_keys:
                    raise ValueError(
                        'Member {} has different addressable keys from other Members: got {}, expected {}.'.format(
                            key,
                            sorted(value._addressable.keys()),
                            sorted(allowed_keys),
                        ),
                    )

                # Check that all Members have the same data for extra_homomorphic.
                if homomorphic_extras is _default_set:
                    homomorphic_extras = set(value._extra_homomorphic.keys())
                elif set(value._extra_homomorphic.keys()) != homomorphic_extras:
                    raise ValueError(
                        'Member {} has different extra keys; got {}; expected {}.'.format(
                            key,
                            sorted(value._extra_homomorphic.keys()),
                            sorted(homomorphic_extras),
                        ),
                    )

                # Check reverse mappings across the whole set of Members.
                for item in value._addressable.values():
                    if item in reversed_addressable:
                        error = 'another member\'s name'
                        if item not in classdict:
                            error = 'an attribute of Member {}'.format(
                                next(k for k, v in iteritems(classdict) if v is reversed_addressable[item])
                            )
                        raise ValueError(
                            'Attribute value "{}" of Member {} is ambiguous with {}.'.format(item, key, error)
                        )
                    reversed_addressable[item] = value
                reversed_addressable[key] = value

            # Callables are 'special' in that they get bound rather than member'd by the enum.
            elif key not in ('__module__', '__metaclass__', '__doc__', '__qualname__', '_order_', '_ignore_')\
                    and not (callable(value) or isinstance(value, classmethod)):
                raise ValueError('{} is not a Member'.format(value))

        for internal_key in {'_reversed'} | allowed_keys:
            if internal_key in classdict:
                raise ValueError('Key {} is not allowed.'.format(internal_key))

        classdict['_reversed'] = lambda _: reversed_addressable
        for key in allowed_keys | homomorphic_extras:
            # Have to call a function so the key gets copied and isn't closure-mutable.
            classdict[key] = metacls._pgetter(key)

        return super(_MatrixEnumMeta, metacls).__new__(metacls, cls, bases, classdict)

    def __call__(cls, value, names=None, *args, **kwargs):
        if names is None:
            # Easiest way to get access to the class field without edge-casing classes with no enum elements is to
            # iterate.
            for item in cls:
                maybe_value = item._reversed().get(value, None)
                if maybe_value is not None:
                    value = maybe_value
                break

        return super(_MatrixEnumMeta, cls).__call__(value, *args, **kwargs)

    def __contains__(cls, value):
        # Enable `in` checks using the Member values by using the same logic as the constructor
        try:
            cls(value)
            return True
        except ValueError:
            return False


class MatrixEnum(with_metaclass(_MatrixEnumMeta, Enum)):
    """
    Enum that can contain multiple data attributes per member, and for which values can be looked up
    using any value in the data.

    All elements must be Members.

    This class exists to solve the multi-way data association issue that emerges when using constants. Say you are
    mapping between a database integer constant and a UI-side short string (e.g. 1: 'one'). Typically, variables for
    the database enum are derived from a range, like 'ONE, TWO = range(2)', and then tracked using a mapping like
    'SHORT_NAMES = { ONE: 'one' }'. Reversing the mapping can be a hassle if lookups need to go the other direction, and
    things get much stickier if a third attribute (say "long form description") is added to the mix: additional mapping
    constants are necessary, with any needed reverse-lookups. Not only does the code get duplicated, but it becomes very
    easy to add a new constant to one mapping and forget to add it to others, risking bugs.

    The MatrixEnum class allows you to quickly (O(1)) access enum members by any attribute. In order for these
    accesses to be unambiguous, every attribute of every Member must be unique across the whole enum. This behavior is
    validated at class-compile time (which costs a bit of computation; as a result it is not recommended to
    programmatically redeclare subclasses of MatrixEnum).

    To add non-unique member values, use the `extra` method of the Member class.
    These values can be accessed, but CANNOT be used to lookup an Enum members.
    Note: All fields in extras must be present across ALL members.
    If you need different fields on different members you may need a separate
    mapping object, separate functions on the enum class, or a more advanced Enum.
    """
