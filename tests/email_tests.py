"""
    Tests for the :mod:`regression_tests.email` module.
"""

import unittest
from unittest import mock

from regression_tests.commit_results import CommitResults
from regression_tests.email import Email
from regression_tests.email import prepare_email
from regression_tests.email import send_email
from regression_tests.test_results import TestsResults
from tests import WithPatching
from tests.git_tests import create_commit
from tests.retdec_builder_tests import create_build_info
from tests.test_results_tests import create_test_results


def create_email(subject='Subject', from_addr='from@addr.com',
                 to_addr='to@addr.com', reply_to_addr='reply_to@addr.com',
                 cc_addr='cc@addr.com', body='Body'):
    """Creates a new `Email` from the given parameters."""
    return Email(
        subject=subject,
        from_addr=from_addr,
        to_addr=to_addr,
        reply_to_addr=reply_to_addr,
        cc_addr=cc_addr,
        body=body
    )


class EmailTests(unittest.TestCase):
    """Tests for `Email`."""

    def test_subject_is_accessible_after_creation(self):
        email = Email(subject='my subject')
        self.assertEqual(email.subject, 'my subject')

    def test_subject_can_be_changed_after_creation(self):
        email = Email()
        email.subject = 'new subject'
        self.assertEqual(email.subject, 'new subject')

    def test_subject_is_empty_after_creation(self):
        email = Email()
        self.assertEqual(len(email.subject), 0)

    def test_from_addr_is_accessible_after_creation(self):
        email = Email(from_addr='me@me.com')
        self.assertEqual(email.from_addr, 'me@me.com')

    def test_from_addr_can_be_changed_after_creation(self):
        email = Email()
        email.from_addr = 'him@him.net'
        self.assertEqual(email.from_addr, 'him@him.net')

    def test_from_addr_is_empty_after_creation(self):
        email = Email()
        self.assertEqual(len(email.from_addr), 0)

    def test_to_addr_is_accessible_after_creation(self):
        email = Email(to_addr='me@me.com')
        self.assertEqual(email.to_addr, 'me@me.com')

    def test_to_addr_can_be_changed_after_creation(self):
        email = Email()
        email.to_addr = 'him@him.net'
        self.assertEqual(email.to_addr, 'him@him.net')

    def test_to_addr_is_empty_after_creation(self):
        email = Email()
        self.assertEqual(len(email.to_addr), 0)

    def test_sendmail_to_addrs_is_empty_when_there_is_no_to_addr(self):
        email = Email()
        self.assertEqual(email.sendmail_to_addrs, [])

    def test_sendmail_to_addrs_returns_singleton_list_when_there_is_only_to_addr(self):
        email = Email(to_addr='me@me.com')
        self.assertEqual(email.sendmail_to_addrs, ['me@me.com'])

    def test_sendmail_to_addrs_returns_two_addresses_when_there_is_to_addr_and_cc_addr(self):
        email = Email(to_addr='me@me.com', cc_addr='him@him.net')
        self.assertEqual(email.sendmail_to_addrs, ['me@me.com', 'him@him.net'])

    def test_reply_to_addr_is_accessible_after_creation(self):
        email = Email(reply_to_addr='me@me.com')
        self.assertEqual(email.reply_to_addr, 'me@me.com')

    def test_reply_to_addr_can_be_changed_after_creation(self):
        email = Email()
        email.reply_to_addr = 'him@him.net'
        self.assertEqual(email.reply_to_addr, 'him@him.net')

    def test_reply_to_addr_is_empty_after_creation(self):
        email = Email()
        self.assertEqual(len(email.reply_to_addr), 0)

    def test_cc_addr_is_accessible_after_creation(self):
        email = Email(cc_addr='me@me.com')
        self.assertEqual(email.cc_addr, 'me@me.com')

    def test_cc_addr_can_be_changed_after_creation(self):
        email = Email()
        email.cc_addr = 'him@him.net'
        self.assertEqual(email.cc_addr, 'him@him.net')

    def test_cc_addr_is_empty_after_creation(self):
        email = Email()
        self.assertEqual(len(email.cc_addr), 0)

    def test_body_is_accessible_after_creation(self):
        email = Email(body='my body')
        self.assertEqual(email.body, 'my body')

    def test_body_can_be_changed_after_creation(self):
        email = Email()
        email.body = 'new body'
        self.assertEqual(email.body, 'new body')

    def test_body_is_empty_after_creation(self):
        email = Email()
        self.assertEqual(len(email.body), 0)

    def test_as_string_returns_correct_value(self):
        email = Email(
            subject='my subject',
            from_addr='me@me.com',
            to_addr='him@him.net',
            reply_to_addr='her@her.org',
            cc_addr='someone@something.net'
        )
        as_string = email.as_string
        self.assertIn('Content-Type: text/plain; charset="utf-8"', as_string)
        self.assertIn('my subject', as_string)
        self.assertIn('From: me@me.com', as_string)
        self.assertIn('To: him@him.net', as_string)
        self.assertIn('Reply-To: her@her.org', as_string)
        self.assertIn('CC: someone@something.net', as_string)


class SendEmailTests(unittest.TestCase, WithPatching):
    """Tests for `send_email()`."""

    def setUp(self):
        # Patch smtplib.SMTP to return our mock server so we can test the
        # sending in isolation.
        self.server = mock.Mock()
        self.smtplib_SMTP_mock = mock.Mock()
        self.smtplib_SMTP_mock.return_value = self.server
        self.patch(
            'regression_tests.email.smtplib.SMTP',
            self.smtplib_SMTP_mock
        )

    def test_sends_email_correctly(self):
        FROM_ADDR = 'me@me.com'
        TO_ADDR = 'him@him.net'
        email = Email(from_addr=FROM_ADDR, to_addr=TO_ADDR)
        SMTP_SERVER = 'smtp.domain.com'
        SMTP_PORT = 25
        SMTP_USER = 'user'
        SMTP_PASS = 'pass'

        send_email(email, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS)

        self.smtplib_SMTP_mock.assert_called_once_with(SMTP_SERVER, SMTP_PORT)
        self.server.starttls.assert_called_once_with()
        self.server.login.assert_called_once_with(SMTP_USER, SMTP_PASS)
        self.server.sendmail.assert_called_once_with(
            FROM_ADDR,
            [TO_ADDR],
            email.as_string
        )
        self.server.quit.assert_called_once_with()

    def scenario_does_not_use_auth(self, smtp_user):
        email = Email(from_addr='him@him.net', to_addr='me@me.com')

        send_email(email, 'smtp.domain.com', 25, smtp_user=smtp_user, smtp_pass='xxx')

        self.assertFalse(self.server.starttls.called)
        self.assertFalse(self.server.login.called)

    def test_does_not_use_auth_if_smtp_user_is_none(self):
        self.scenario_does_not_use_auth(smtp_user=None)

    def test_does_not_use_auth_if_smtp_user_is_empty_string(self):
        self.scenario_does_not_use_auth(smtp_user='')


class PrepareEmailTests(unittest.TestCase):
    """Tests for `prepare_email()`."""

    def setUp(self):
        self.commit = create_commit(
            author='Petr Zemek',
            email='petr.zemek@avast.com'
        )
        self.subject_prefix = 'PREFIX'
        self.web_url = 'http://tests.net'
        self.wiki_page_url = 'http://wiki.net'

    def test_sets_correct_addresses_and_urls(self):
        commit_results = CommitResults(
            self.commit, TestsResults(), create_build_info()
        )

        email = prepare_email(
            commit_results,
            self.subject_prefix,
            self.web_url,
            self.wiki_page_url
        )

        self.assertEqual(email.to_addr, 'Petr Zemek <petr.zemek@avast.com>')
        self.assertRegex(email.subject, r'^{}'.format(self.subject_prefix))
        self.assertIn(self.web_url, email.body)
        self.assertIn(self.wiki_page_url, email.body)

    def test_creates_correct_body_when_build_failed(self):
        commit_results = CommitResults(
            self.commit,
            TestsResults(),
            create_build_info(succeeded=False)
        )

        email = prepare_email(
            commit_results,
            self.subject_prefix,
            self.web_url,
            self.wiki_page_url
        )

        self.assertRegex(email.body, r'build failed')

    def test_creates_correct_body_when_one_test_failed_in_one_module(self):
        commit_results = CommitResults(
            self.commit,
            TestsResults([
                create_test_results(
                    module_name='module1',
                    run_tests=3,
                    failed_tests=1
                )
            ]),
            create_build_info(succeeded=True)
        )

        email = prepare_email(
            commit_results,
            self.subject_prefix,
            self.web_url,
            self.wiki_page_url
        )

        self.assertRegex(email.body, r'1 test failed in the following module:')
        self.assertRegex(email.body, r'module1')

    def test_creates_correct_email_when_two_tests_failed_in_one_module(self):
        commit_results = CommitResults(
            self.commit,
            TestsResults([
                create_test_results(
                    module_name='module1',
                    case_name='Test (input.exe)',
                    run_tests=3,
                    failed_tests=2
                ),
            ]),
            create_build_info(succeeded=True)
        )

        email = prepare_email(
            commit_results,
            self.subject_prefix,
            self.web_url,
            self.wiki_page_url
        )

        self.assertRegex(email.body, r'2 tests failed in the following module:')
        self.assertRegex(email.body, r'module1')

    def test_creates_correct_email_when_two_tests_failed_in_two_modules(self):
        commit_results = CommitResults(
            self.commit,
            TestsResults([
                create_test_results(
                    module_name='module1',
                    case_name='Test (input.exe)',
                    run_tests=3,
                    failed_tests=1
                ),
                create_test_results(
                    module_name='module2',
                    case_name='Test (input.exe)',
                    run_tests=1,
                    failed_tests=1
                )
            ]),
            create_build_info(succeeded=True)
        )

        email = prepare_email(
            commit_results,
            self.subject_prefix,
            self.web_url,
            self.wiki_page_url
        )

        self.assertRegex(email.body, r'2 tests failed in the following modules:')
        self.assertRegex(email.body, r'module1')
        self.assertRegex(email.body, r'module2')

    def test_creates_correct_email_when_no_test_failed(self):
        commit_results = CommitResults(
            self.commit,
            TestsResults([
                create_test_results(run_tests=3, failed_tests=0)
            ]),
            create_build_info(succeeded=True)
        )

        email = prepare_email(
            commit_results,
            self.subject_prefix,
            self.web_url,
            self.wiki_page_url
        )

        self.assertRegex(email.body, r'unknown failure')
