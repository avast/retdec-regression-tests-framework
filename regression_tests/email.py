"""
    Emailing support.
"""

import email.mime.text
import smtplib

from regression_tests.utils.format import format_date


class Email:
    """Representation of an email."""

    def __init__(self, *, subject=None, from_addr=None, to_addr=None,
                 reply_to_addr=None, cc_addr=None, body=None):
        """
        :param str subject: Email subject.
        :param str from_addr: Sender address.
        :param str to_addr: Receiver address.
        :param str reply_to_addr: Address to which replies should be sent.
        :param str cc_addr: Address to which a copy of this email should be
                            sent.
        :param str body: Email body.
        """
        self.subject = subject
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.reply_to_addr = reply_to_addr
        self.cc_addr = cc_addr
        self.body = body

    @property
    def subject(self):
        """Email subject."""
        return self._subject

    @subject.setter
    def subject(self, subject):
        self._subject = subject or ''

    @property
    def from_addr(self):
        """Sender address."""
        return self._from_addr

    @from_addr.setter
    def from_addr(self, from_addr):
        self._from_addr = from_addr or ''

    @property
    def to_addr(self):
        """Receiver address."""
        return self._to_addr

    @to_addr.setter
    def to_addr(self, to_addr):
        self._to_addr = to_addr or ''

    @property
    def sendmail_to_addrs(self):
        """A list of addresses to be used when sending the email through
        SMTP.sendmail.

        These addresses are used to construct the message envelope used by the
        transport agents. See
        https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
        for more details.
        """
        addrs = []
        if self.to_addr:
            addrs.append(self.to_addr)
        # We have to include also copies (CC); otherwise, copies won't be sent.
        if self.cc_addr:
            addrs.append(self.cc_addr)
        return addrs

    @property
    def reply_to_addr(self):
        """Address to which replies should be sent."""
        return self._reply_to_addr

    @reply_to_addr.setter
    def reply_to_addr(self, reply_to_addr):
        self._reply_to_addr = reply_to_addr or ''

    @property
    def cc_addr(self):
        """Address to which a copy of this email should be sent."""
        return self._cc_addr

    @cc_addr.setter
    def cc_addr(self, cc_addr):
        self._cc_addr = cc_addr or ''

    @property
    def body(self):
        """Email body."""
        return self._body

    @body.setter
    def body(self, body):
        self._body = body or ''

    @property
    def as_string(self):
        """A string representation of the email."""
        mail = email.mime.text.MIMEText(self.body, _charset='utf-8')
        mail['Subject'] = self.subject
        mail['From'] = self.from_addr
        mail['To'] = self.to_addr
        mail['Reply-To'] = self.reply_to_addr
        mail['CC'] = self.cc_addr
        return mail.as_string()


def send_email(email, smtp_server, smtp_port, smtp_user, smtp_pass):
    """Sends the given email by using the given server and credentials.

    :param Email email: Email to be sent.
    :param str smtp_server: Address of the SMTP server to be used.
    :param int smtp_port: Port of the SMTP server.
    :param str smtp_user: User name to be used for authentication.
    :param str smtp_pass: Password to be used for authentication.

    Set `smtp_user` to ``None`` or to the empty string to disable
    authentication.
    """
    server = smtplib.SMTP(smtp_server, smtp_port)
    if smtp_user:
        server.starttls()
        server.login(smtp_user, smtp_pass)
    server.sendmail(email.from_addr, email.sendmail_to_addrs, email.as_string)
    server.quit()


def prepare_email(commit_results, email_subject_prefix, web_url, wiki_page_url):
    """Prepares an email and returns it.

    :param CommitResults commit_results: Results to be used as source of
                                         information.
    :param str email_subject_prefix: Prefix for the email.
    :param str web_url: URL to the main web page.
    :param str wiki_page_url: URL to the wiki page.
    """
    commit = commit_results.commit

    to_addr = '{} <{}>'.format(commit.author, commit.email)

    subject = '{} Regression tests failed for commit {}'.format(
        email_subject_prefix, commit.short_hash())

    body = 'Hello {},\n'.format(commit.author)
    body += '\n'
    body += 'your commit ' + commit.short_hash() + ' may have introduced the ' +\
        'following errors due to which regression tests have failed:\n'
    body += '\n'
    if commit_results.build_has_failed():
        body += ' - build failed\n'
    elif commit_results.has_failed_tests():
        failed_module_names = commit_results.failed_module_names
        body += ' - {} test{} failed in the following module{}:\n'.format(
            commit_results.failed_tests,
            's' if commit_results.failed_tests != 1 else '',
            's' if len(failed_module_names) != 1 else ''
        )
        body += '\n'
        for module_name in failed_module_names:
            body += '     {}\n'.format(module_name)
    else:
        body += ' - unknown failure\n'
    body += '\n'
    body += 'Details:\n'
    body += '\n'
    body += '   Commit:  {}\n'.format(commit.hash)
    body += '   Author:  {} <{}>\n'.format(commit.author, commit.email)
    body += '   Subject: {}\n'.format(commit.subject)
    body += '   Date:    {}\n'.format(format_date(commit.date))
    body += '\n'
    body += 'Please, verify that there is indeed an error in the commit' +\
        ' above and if so, fix the problem as soon as possible.\n'
    body += '\n'
    # The space after "--" is really needed (see
    # https://en.wikipedia.org/wiki/Signature_block#Signatures_in_Usenet_postings).
    body += '-- \n'
    body += 'Web:  {}\n'.format(web_url)
    body += 'Wiki: {}\n'.format(wiki_page_url)

    return Email(
        subject=subject,
        to_addr=to_addr,
        body=body
    )
