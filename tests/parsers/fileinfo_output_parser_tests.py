"""
    Tests for the :module`regression_tests.parsers.fileinfo_output_parser`
    module.
"""

import unittest

from regression_tests.parsers.text_parser import Text
from regression_tests.parsers.fileinfo_output_parser import FileinfoOutput
from regression_tests.parsers.fileinfo_output_parser import parse


class ParseTests(unittest.TestCase):
    """Tests for `parse()`."""

    def test_returns_fileinfo_output_from_string(self):
        output = parse('output')
        self.assertIsInstance(output, FileinfoOutput)

    def test_returned_object_is_like_text(self):
        output = parse('output')
        self.assertIsInstance(output, Text)


class FileinfoOutputTests(unittest.TestCase):
    """Tests for `FileinfoOutput` parsing of plain output."""

    def test_returns_value_of_key_that_exists_and_has_value(self):
        output = FileinfoOutput("""
            File format:PE
        """)
        self.assertEqual(output['File format'], 'PE')

    def test_raises_exception_when_key_does_not_exist(self):
        output = FileinfoOutput('')
        with self.assertRaisesRegex(KeyError, '.*File format.*'):
            output['File format']

    def test_returns_list_of_values_for_key_that_appears_multiple_times(self):
        # The following example is contrived. Currently, the only key that can
        # actually have multiple values is 'Detected compiler/packer'. This key
        # is tested in other tests.
        output = FileinfoOutput("""
            Architecture: ARM
            Architecture: x86
        """)
        self.assertEqual(output['Architecture'], ['ARM', 'x86'])

    def test_returns_list_for_detected_compiler_or_packer_when_multiple_occurrences(self):
        output = FileinfoOutput("""
            Detected compiler/packer:GCC
            Detected compiler/packer:Clang
        """)
        self.assertEqual(output['Detected compiler/packer'], ['GCC', 'Clang'])

    def test_returns_list_for_detected_compiler_or_packer_even_if_only_single_occurrence(self):
        output = FileinfoOutput("""
            Detected compiler/packer:GCC
        """)
        self.assertEqual(output['Detected compiler/packer'], ['GCC'])

    def test_returns_list_for_detected_compiler_or_packer_even_if_no_occurrence(self):
        output = FileinfoOutput('')
        self.assertEqual(output['Detected compiler/packer'], [])

    def test_ignores_whitespace_before_and_after_key_and_value(self):
        output = FileinfoOutput("""
            \t  File format \t   :   \t PE  \t
        """)
        self.assertEqual(output['File format'], 'PE')

    def test_ignores_lines_not_formed_by_key_and_value_pairs(self):
        output = FileinfoOutput("""
            xxx
            File format:PE
            xxx
            File class:32-bit
            xxx
        """)
        self.assertEqual(output['File format'], 'PE')
        self.assertEqual(output['File class'], '32-bit')

    def test_real_verbose_output_is_parsed_correctly(self):
        output = FileinfoOutput("""
            Input file               : test.exe
            File format              : PE
            File class               : 32-bit
            File type                : Executable file
            Architecture             : x86 (or later and compatible)
            Endianness               : Little endian
            Image base address       : 0x400000
            Entry point address      : 0x4014e0
            Entry point offset       : 0x8e0
            Entry point section name : .text
            Entry point section index: 0
            Bytes on entry point     : 83ec0cc7053ca0400000000000e8
            Detected compiler/packer : GCC (mingw32-x86-pe) (4.7.3)
            Detected compiler/packer : GCC (4.7.3)
            Original language        : C

            File status                            : PE32
            [...]
            File flags                             : 0000000100000111 (rvl3)

            Data directories
            ----------------

            i     type                          address     size
            ----------------------------------------------------------
            0     Export table                  0           0
            [..]
            1309  __imp__EnterCriticalSection@4     SIMPLE       4          312

            Relocation table
            ----------------
            Number of relocations                           : 0
        """)
        self.assertEqual(output['Input file'], 'test.exe')
        self.assertEqual(
            output['Detected compiler/packer'],
            ['GCC (mingw32-x86-pe) (4.7.3)', 'GCC (4.7.3)']
        )
        self.assertEqual(output['File flags'], '0000000100000111 (rvl3)')
        self.assertEqual(output['Number of relocations'], '0')

    def test_operator_contains_searches_in_output_correctly(self):
        output = FileinfoOutput("""
            File format:PE
        """)
        self.assertIn('File format:PE', output)
        self.assertIn('PE', output)


class FileinfoJSONOutputTests(unittest.TestCase):
    """Tests for `FileinfoOutput` parsing of JSON output."""

    def test_returns_value_of_key_that_exists(self):
        output = FileinfoOutput("""
            {
                "inputFile" : "file.exe"
            }
        """)
        self.assertEqual(output['inputFile'], 'file.exe')

    def test_raises_exception_when_key_does_not_exist(self):
        output = FileinfoOutput('{}')
        with self.assertRaisesRegex(KeyError, '.*xxx.*'):
            output['xxx']

    def test_raises_exception_when_json_is_invalid(self):
        output = FileinfoOutput('{')
        with self.assertRaises(ValueError):
            output['xxx']

    def test_real_output_is_parsed_correctly(self):
        output = FileinfoOutput("""
            {
                "architecture" : "x86",
                "entryPointAddress" : "0x4014e0",
                "inputFile": "file.exe",
                "languages" : [
                    {
                        "bytecode" : false,
                        "name" : "C"
                    }
                ],
                "tools" : [
                   {
                       "heuristics" : false,
                       "identicalSignificantNibbles" : 169,
                       "name" : "GCC (mingw32-x86-pe)",
                       "percentage" : 100,
                       "totalSignificantNibbles" : 169,
                       "version" : "4.7.3"
                   },
                   {
                       "heuristics" : true,
                       "identicalSignificantNibbles" : 0,
                       "name" : "GCC",
                       "percentage" : 0,
                       "totalSignificantNibbles" : 0,
                       "version" : "4.7.3"
                   }
                ]
            }
        """)
        self.assertEqual(output['inputFile'], 'file.exe')
        self.assertEqual(output['entryPointAddress'], '0x4014e0')
        self.assertEqual(len(output['languages']), 1)
        self.assertEqual(len(output['tools']), 2)
        self.assertEqual(output['tools'][1]['name'], 'GCC')
        self.assertEqual(output['tools'][1]['percentage'], 0)

    def test_operator_contains_searches_in_output_correctly(self):
        output = FileinfoOutput("""
            {
                "fileFormat": "pe"
            }
        """)
        self.assertIn('fileFormat', output)
        self.assertNotIn('pe', output)
