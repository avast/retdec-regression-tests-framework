"""
    Parsing of the output from fileinfo.
"""

import json
import re

from regression_tests.parsers.text_parser import Text


def parse(output):
    """Parses the given output from fileinfo (`str`).

    :returns: Parsed representation of the given output
              (:class:`FileinfoOutput`).
    """
    return FileinfoOutput(output)


class FileinfoOutput(Text):
    """Parsed output from fileinfo.

    Instances of this class behave like strings with additional properties and
    methods. That is, you can access the output in its raw form (as `str`), but
    also use methods that operate on the parsed representation of the output.

    The parsed representation provides a dictionary-like access to the output.
    The precise structure and keys of the dictionary depends on the type of the
    output that fileinfo produced. By default, it produces plain text output
    (the ``-p/--plain`` parameter, which is the default one):

    .. code-block:: text

        $ fileinfo file.exe
        Input file               : file.exe
        File format              : PE
        File class               : 32-bit
        ...

    Keys are then words from the first column, before ``:``, like ``'Input
    file'``.

    The other supported format is JSON, which is selected by the ``-j/--json``
    parameter:

    .. code-block:: text

        $ fileinfo -j file.exe
        {
            "architecture" : "x86",
            "endianness" : "Little endian",
            ...
        }

    Keys are then, of course, the keys from the parsed JSON, like
    ``'architecture'``.

    For simplicity, in the remainder of this description, we assume that the
    output was plain text (the default one). Tests for the JSON output can be
    written analogically.

    For example, consider a variable ``fileinfo_output`` that stores some
    parsed output from fileinfo. Then, you can perform the following checks:

    .. code-block:: python

        assert fileinfo_output['File format'] == 'PE'
        # or (better)
        self.assertEqual(fileinfo_output['File format'], 'PE')

    You can access all ``key:value`` pairs that appear in the fileinfo output,
    not just ``'File format'``:

    .. code-block:: python

        self.assertEqual(fileinfo_output['Architecture'], 'ARM')

    When there is a key that appears multiple times in the output (like
    ``'Detected compiler/packer'``), it returns a list of values instead of a
    single value. For example, assume that ``fileinfo_output`` contains the
    following lines:

    .. code-block:: text

        Detected compiler/packer : GCC (mingw32-x86-pe) (4.7.3)
        Detected compiler/packer : GCC (4.7.3)

    Then,

    .. code-block:: python

        self.assertEqual(
            fileinfo_output['Detected compiler/packer'],
            ['GCC (mingw32-x86-pe) (4.7.3)', 'GCC (4.7.3)']
        )

    The ``'Detected compiler/packer'`` key is special because it's value is
    always a list, even if it appears only once in the output (or does not
    appear at all, in which case the list is empty).

    Of course, if you want, you can still work with ``fileinfo_output`` as if
    it was `str`:

    .. code-block:: python

        assert 'PE' in fileinfo_output

    or :class:`.Text`:

    .. code-block:: python

        assert fileinfo_output.contains('.*GCC.*4\\.7.*')

    The behavior of the ``in`` operator depends on the format of the output.
    For plain-text output, it behaves like regular ``in`` for strings,
    searching for a substring. For JSON output, it behaves like ``in`` for
    dictionaries, searching for a specific key in the top-level JSON object.
    Let us assume we have the following output:

    .. code-block:: text

        Input file               : file.exe
        File format              : PE

    The next two tests would pass for this output:

    .. code-block:: python

        self.assertIn('Input file', fileinfo_output)
        self.assertIn('file.exe', fileinfo_output)

    Let us take the same output, but this time in the JSON format:

    .. code-block:: text

        {
            "inputFile" : "file.exe",
            "fileFormat" : "pe"
        }

    The following tests would pass (notice ``assertNotIn`` for second
    condition):

    .. code-block:: python

        self.assertIn('inputFile', fileinfo_output)
        self.assertNotIn('file.exe', fileinfo_output)
    """

    def _parse_output_unless_already_parsed(self):
        """Parses the output from fileinfo unless it has already been parsed.
        """
        if not self._output_parsed():
            self._parse_output()

    def _output_parsed(self):
        """Has the output been parsed?"""
        return hasattr(self, '_parsed_output')

    def _parse_output(self):
        """Parses the output from fileinfo and stores it into
        ``self._parsed_output``.
        """
        if self._is_output_in_json_format():
            self._parsed_output = self._parse_json_output()
        else:
            self._parsed_output = self._parse_plain_text_output()

    def _is_output_in_json_format(self):
        """Is the output in the JSON format?"""
        return re.match(r'^\s*{', self)

    def _parse_json_output(self):
        """Parses the output as JSON and returns it as a dictionary."""
        return json.loads(self)

    def _parse_plain_text_output(self):
        """Parses the output as plain text and returns it as a dictionary."""
        parsed_output = {}

        # When a key appears multiple times, store the values into a list.
        #
        # We want 'Detected compiler/packer' to always return a list, even if
        # there are no occurrences.
        parsed_output['Detected compiler/packer'] = []

        for line in self.split('\n'):
            m = re.fullmatch(r'([^:]+):(.+)', line)
            if m is not None:
                key = m.group(1).strip()
                value = m.group(2).strip()
                if key not in parsed_output:
                    parsed_output[key] = value
                elif isinstance(parsed_output[key], list):
                    parsed_output[key].append(value)
                else:
                    parsed_output[key] = [parsed_output[key], value]
        return parsed_output

    def __contains__(self, key):
        if self._is_output_in_json_format():
            self._parse_output_unless_already_parsed()
            return key in self._parsed_output
        else:
            return super().__contains__(key)

    def __getitem__(self, key):
        self._parse_output_unless_already_parsed()
        return self._parsed_output[key]
