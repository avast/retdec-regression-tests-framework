"""
    Tests for the :module`regression_tests.parsers.config_parser` module.
"""

import unittest

from regression_tests.parsers.config_parser import Config
from regression_tests.parsers.config_parser import parse


class ParseTests(unittest.TestCase):
    """Tests for `parse()`."""

    def test_returns_config_from_string(self):
        config = parse('{}')
        self.assertIsInstance(config, Config)

    def test_returned_object_is_like_string(self):
        config = parse('{}')
        self.assertIsInstance(config, str)


class ConfigTests(unittest.TestCase):
    """Tests for `Config`."""

    def test_contains_returns_true_if_regexp_is_found(self):
        config = Config("""
            {
                "key": "value"
            }
        """)
        self.assertTrue(config.contains(r'"key": "value"'))

    def test_contains_returns_false_if_regexp_is_not_found(self):
        config = Config('{}')
        self.assertFalse(config.contains(r'test'))

    def test_json_returns_underlying_dict(self):
        config = Config("""
            {
                "key": "value"
            }
        """)
        self.assertEqual(config.json['key'], 'value')

    def test_exception_is_raised_when_config_cannot_be_parsed(self):
        with self.assertRaises(ValueError):
            Config('#')

    def test_is_statically_linked_returns_true_when_func_is_statically_linked(self):
        config = Config("""
            {
                "functions" : [
                    {
                        "name" : "my_func",
                        "fncType" : "staticallyLinked"
                    }
                ]
            }
        """)
        self.assertTrue(config.is_statically_linked('my_func'))

    def test_is_statically_linked_returns_false_when_func_is_not_statically_linked(self):
        config = Config("""
            {
                "functions" : [
                    {
                        "name" : "my_func",
                        "fncType" : "dynamicallyLinked"
                    }
                ]
            }
        """)
        self.assertFalse(config.is_statically_linked('my_func'))

    def test_is_statically_linked_returns_true_when_address_matches(self):
        config = Config("""
            {
                "functions" : [
                    {
                        "name" : "my_func",
                        "fncType" : "staticallyLinked",
                        "startAddr" : 1000
                    }
                ]
            }
        """)
        self.assertTrue(config.is_statically_linked('my_func', 1000))

    def test_is_statically_linked_returns_false_when_address_does_not_match(self):
        config = Config("""
            {
                "functions" : [
                    {
                        "name" : "my_func",
                        "fncType" : "staticallyLinked",
                        "startAddr" : 444
                    }
                ]
            }
        """)
        self.assertFalse(config.is_statically_linked('my_func', 1000))

    def test_raises_assertion_error_when_there_are_no_funcs(self):
        config = Config('{}')
        with self.assertRaisesRegex(AssertionError, r'no such function: my_func'):
            config.is_statically_linked('my_func')

    def test_raises_assertion_error_when_there_is_no_such_func(self):
        config = Config("""
            {
                "functions" : []
            }
        """)
        with self.assertRaisesRegex(AssertionError, r'no such function: my_func'):
            config.is_statically_linked('my_func')

    def test_vtables_can_be_indexed_by_numbers(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1", "address" : 1000 },
                    { "name" : "vt2", "address" : 2000 }
                ]
            }
        """)
        self.assertEqual(config.vtables[0].name, 'vt1')
        self.assertEqual(config.vtables[1].address, 2000)

    def test_vtables_can_be_indexed_by_names(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1", "address" : 1000 },
                    { "name" : "vt2", "address" : 2000 }
                ]
            }
        """)
        self.assertEqual(config.vtables['vt1'].address, 1000)
        self.assertEqual(config.vtables['vt2'].address, 2000)

    def test_vtable_names_matches_expected_names(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" },
                    { "name" : "vt2" },
                    { "name" : "vt3" }
                ]
            }
        """)
        self.assertEqual(config.vtable_names, ['vt1', 'vt2', 'vt3'])

    def test_vtable_names_return_empty_list_if_vtables_empty(self):
        config = Config("""
            {
            }
        """)
        self.assertEqual(config.vtable_names, [])

    def test_vtable_count_matches_number_of_vtables(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" },
                    { "name" : "vt2" },
                    { "name" : "vt3" }
                ]
            }
        """)
        self.assertEqual(config.vtable_count, 3)

    def test_vtable_count_returns_zero_if_vtables_empty(self):
        config = Config("""
            {
            }
        """)
        self.assertEqual(config.vtable_count, 0)

    def test_has_vtables_returns_true_when_given_vtables_present(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" },
                    { "name" : "vt2" },
                    { "name" : "vt3" }
                ]
            }
        """)
        self.assertTrue(config.has_vtables('vt1'))
        self.assertTrue(config.has_vtables('vt1', 'vt2'))
        self.assertTrue(config.has_vtables('vt1', 'vt2', 'vt3'))

    def test_has_vtables_returns_true_when_vtables_present_and_no_vtables_are_given(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" }
                ]
            }
        """)
        self.assertTrue(config.has_vtables())

    def test_has_vtables_returns_false_when_given_vtables_not_present(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" },
                    { "name" : "vt2" },
                    { "name" : "vt3" }
                ]
            }
        """)
        self.assertFalse(config.has_vtables('vt4'))
        self.assertFalse(config.has_vtables('vt1', 'vt4'))

    def test_has_vtables_returns_false_when_no_vtables_present(self):
        config = Config("""
            {
                "vtables" : []
            }
        """)
        self.assertFalse(config.has_vtables())

    def test_has_no_vtables_returns_true_when_vtables_empty(self):
        config = Config("""
            {
            }
        """)
        self.assertTrue(config.has_no_vtables())

    def test_has_no_vtables_returns_false_when_vtables_not_empty(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" }
                ]
            }
        """)
        self.assertFalse(config.has_no_vtables())

    def test_has_just_vtables_returns_true_when_all_vtables_enumerated(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" },
                    { "name" : "vt2" },
                    { "name" : "vt3" }
                ]
            }
        """)
        self.assertTrue(config.has_just_vtables('vt3', 'vt2', 'vt1'))

    def test_has_just_vtables_returns_false_when_some_vtables_not_enumerated(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" },
                    { "name" : "vt2" },
                    { "name" : "vt3" }
                ]
            }
        """)
        self.assertFalse(config.has_just_vtables('vt1', 'vt3'))

    def test_has_vtable_returns_true_when_vtable_exists(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" },
                    { "name" : "vt2" }
                ]
            }
        """)
        self.assertTrue(config.has_vtable('vt2'))

    def test_has_vtable_returns_false_when_vtable_does_not_exist(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1" }
                ]
            }
        """)
        self.assertFalse(config.has_vtable('vt3'))

    def test_has_vtable_on_address_returns_true_when_vtable_on_address_exists(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1", "address" : 1000 },
                    { "name" : "vt2", "address" : 2000 }
                ]
            }
        """)
        self.assertTrue(config.has_vtable_on_address(1000))
        self.assertTrue(config.has_vtable_on_address(2000))

    def test_has_vtable_on_address_returns_false_when_vtable_on_address_does_not_exists(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1", "address" : 1000 },
                    { "name" : "vt2", "address" : 2000 }
                ]
            }
        """)
        self.assertFalse(config.has_vtable_on_address(3000))

    def test_vtable_on_address_returns_vtable_when_it_exists(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1", "address" : 1000 },
                    { "name" : "vt2", "address" : 2000 }
                ]
            }
        """)
        self.assertEqual(config.vtable_on_address(1000).name, 'vt1')

    def test_vtable_on_address_returns_none_when_vtable_does_not_exist(self):
        config = Config("""
            {
                "vtables" : [
                    { "name" : "vt1", "address" : 1000 },
                    { "name" : "vt2", "address" : 2000 }
                ]
            }
        """)
        self.assertEqual(config.vtable_on_address(3000), None)

    def test_vtable_initialized_to_default_values(self):
        config = Config("""
            {
                "vtables" : [
                    {  }
                ]
            }
        """)
        self.assertEqual(config.vtables[0].name, None)
        self.assertEqual(config.vtables[0].address, None)
        self.assertEqual(config.vtables[0].items, [])

    def test_vtable_initialized_to_expected_values(self):
        config = Config("""
            {
                "vtables" : [
                    {
                        "address" : 1000,
                        "items" : [
                            {
                                "address" : 1004,
                                "targetAddress" : 2000,
                                "targetName" : "func_2000"
                            },
                            {
                                "address" : 1008,
                                "targetAddress" : 3000,
                                "targetName" : "func_3000"
                            }
                        ],
                        "name" : "vt1"
                    }
                ]
            }
        """)
        self.assertEqual(config.vtables[0].name, 'vt1')
        self.assertEqual(config.vtables[0].address, 1000)
        self.assertEqual(len(config.vtables[0].items), 2)
        self.assertEqual(config.vtables[0].item_count, 2)
        self.assertEqual(config.vtables[0].item_target_names, ['func_2000', 'func_3000'])

    def test_VtableItem_initialized_to_default_values(self):
        config = Config("""
            {
                "vtables" : [
                    { "items" : [ {} ] }
                ]
            }
        """)
        self.assertEqual(config.vtables[0].items[0].address, None)
        self.assertEqual(config.vtables[0].items[0].target_address, None)
        self.assertEqual(config.vtables[0].items[0].target_name, None)

    def test_Class_initilized_to_expected_values(self):
        config = Config("""
            {
                "classes" : [
                    {
                        "constructors" : [ "c1", "c2", "c3" ],
                        "destructors" : [ "d1" ],
                        "methods" : [ "m1", "m2", "m3" ],
                        "name" : "class1",
                        "superClasses" : [ "class2", "class3" ],
                        "virtualMethods" : [ "v1", "v2", "v3" ],
                        "virtualTables" : [ "vt1", "vt2" ]
                    },
                    {
                        "constructors" : [ "c1", "c2", "c3" ],
                        "destructors" : [ "d1", "d2" ],
                        "methods" : [ "m1", "m2", "m3" ],
                        "name" : "class2",
                        "superClasses" : [ "class1" ],
                        "virtualMethods" : [ "v1", "v2", "v3" ],
                        "virtualTables" : [ "vt2" ]
                    }
                ]
            }
        """)
        self.assertEqual(config.classes[0].name, 'class1')
        self.assertEqual(config.classes[1].name, 'class2')

        self.assertEqual(config.classes['class1'].name, 'class1')
        self.assertEqual(config.classes['class2'].name, 'class2')

        class1 = config.classes['class1']

        self.assertEqual(class1.constructors, ["c1", "c2", "c3"])
        self.assertEqual(class1.destructors, ["d1"])
        self.assertEqual(class1.methods, ["m1", "m2", "m3"])
        self.assertEqual(class1.superClasses, ["class2", "class3"])
        self.assertEqual(class1.virtualMethods, ["v1", "v2", "v3"])
        self.assertEqual(class1.virtualTables, ["vt1", "vt2"])

        self.assertEqual(config.classes_names, ['class1', 'class2'])

        self.assertEqual(config.classes_count, 2)
