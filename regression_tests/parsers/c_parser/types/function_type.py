"""
    A function type.
"""

from regression_tests.parsers.c_parser.types.type import Type


class FunctionType(Type):
    """A function type."""

    def is_function(self):
        """Returns ``True``."""
        return True

    @property
    def return_type(self):
        """Type of the returned values (:class:`.Type`)."""
        return Type._from_clang_type(self._type.get_result())

    @property
    def param_types(self):
        """Types of parameters of the function (list of :class:`.Type`)."""
        param_types = []
        for node in self._type.get_canonical().argument_types():
            param_types.append(Type._from_clang_type(node))
        return param_types

    @property
    def param_count(self):
        """Number of parameters of the function."""
        return len(self.param_types)

    def is_variadic(self):
        """Is the function variadic?

        A function is variadic when it takes a variable number of parameters,
        like ``printf()``.
        """
        return self._type.get_canonical().is_function_variadic()

    def __eq__(self, other):
        return (isinstance(other, FunctionType) and
                self.return_type == other.return_type and
                self.param_types == other.param_types)

    def __hash__(self):
        return hash('function') + hash(self.return_type) + hash(self.param_count)

    def __repr__(self):
        return '<{} return_type={!s} param_types={}>'.format(
            self.__class__.__name__,
            self.return_type,
            '({})'.format(', '.join(map(lambda t: str(t), self.param_types)))
        )
