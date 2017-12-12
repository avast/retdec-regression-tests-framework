"""
    Tests for the :mod:`regression_tests.qos` module.
"""

import unittest

from unittest import mock

from regression_tests.qos import WithQoS


class WithQoSTests(unittest.TestCase):
    """Tests for `WithQoS`."""

    def setUp(self):
        self.obj = mock.MagicMock()

    def test_method_is_called_once_with_correct_arguments_when_no_exception(self):
        qos = WithQoS(self.obj)
        qos.method('a', b='b')
        self.assertEqual(
            self.obj.method.call_args_list,
            [
                mock.call('a', b='b')
            ]
        )

    def test_method_is_called_twice_with_correct_arguments_when_exception_on_first_call(self):
        qos = WithQoS(self.obj)
        self.obj.method.side_effect = [ValueError, None]
        qos.method('a', b='b')
        self.assertEqual(
            self.obj.method.call_args_list,
            [
                mock.call('a', b='b'),
                mock.call('a', b='b')
            ]
        )

    def test_method_returns_correct_return_value(self):
        qos = WithQoS(self.obj)
        self.obj.method.return_value = 42
        self.assertEqual(qos.method(), 42)

    def test_method_is_called_not_called_when_max_tries_is_0(self):
        qos = WithQoS(self.obj, max_tries=0)
        qos.method()
        self.assertFalse(self.obj.method.called)

    def test_method_is_called_once_when_max_tries_is_1_even_if_exception_is_raised(self):
        qos = WithQoS(self.obj, max_tries=1)
        self.obj.method.side_effect = ValueError
        with self.assertRaises(ValueError):
            qos.method()
        self.assertEqual(
            self.obj.method.call_args_list,
            [
                mock.call()
            ]
        )

    def test_method_is_called_twice_when_max_tries_is_2_and_exceptions_are_raised(self):
        qos = WithQoS(self.obj, max_tries=2)
        self.obj.method.side_effect = [ValueError, ValueError]
        with self.assertRaises(ValueError):
            qos.method()
        self.assertEqual(
            self.obj.method.call_args_list,
            [
                mock.call(),
                mock.call()
            ]
        )

    def test_waits_for_wait_time_after_each_but_last_try(self):
        qos = WithQoS(self.obj, max_tries=2, wait_time=5)
        self.obj.method.side_effect = [ValueError, ValueError]
        with mock.patch('time.sleep') as sleep_mock:
            with self.assertRaises(ValueError):
                qos.method()
            sleep_mock.assert_called_once_with(5)

    def test_logs_each_but_last_exception_when_raised(self):
        qos = WithQoS(self.obj, max_tries=2)
        self.obj.method.side_effect = [ValueError, ValueError]
        with mock.patch('logging.exception') as log_mock:
            with self.assertRaises(ValueError):
                qos.method()
            log_mock.assert_called_once_with('caught ValueError; will retry')
