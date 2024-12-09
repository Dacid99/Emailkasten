import pytest
from unittest.mock import patch
from email.message import Message
import Emailkasten.mailParsing
import Emailkasten.constants
import datetime

@pytest.fixture(scope='module')
def test_good_mailMessage():
    testMessage = Message()
    testMessage.add_header("Message-ID", 'abcdefgäöüß§')
    testMessage.add_header("Subject", 'This a test SUBJEcT line äöüß§')
    testMessage.add_header("Date", 'Fri, 09 Nov 2001 01:08:47 -0000')
    testMessage.add_header("test", 'test äöüß§')
    testMessage.add_header("multi", 'test')
    testMessage.add_header("multi", 'äöüß§\t')
    testMessage.add_header("multi", '123456')
    return testMessage

@pytest.fixture(scope='module')
def test_special_mailMessage():
    testMessage = Message()
    testMessage.add_header("Subject", 'This a test SUBJEcT line äöüß§ \t ')
    return testMessage

@pytest.fixture(scope='module')
def test_bad_mailMessage():
    testMessage = Message()
    return testMessage

@pytest.fixture(scope='module')
def test_no_mailMessage():
    testMessage = None
    return testMessage


@pytest.mark.parametrize(
    'testHeader, expectedResult',
    [
        ('test äöüß§', "test äöüß§")
    ]
)
@patch('Emailkasten.mailParsing.logger')
def test__decodeHeader(mock_logger, testHeader, expectedResult):
    decodedHeader = Emailkasten.mailParsing._decodeHeader(testHeader)
    assert decodedHeader == expectedResult


@pytest.mark.parametrize(
        'testMailers, expectedResult, warningCalled',
        [
            (["Test äöüß§ <test@testdomain.tld>"], [("Test äöüß§", "test@testdomain.tld")], False),
            (["Test Persön <testtestdomain.tld>"], [("Test Persön", "testtestdomain.tld")], True),
            (["test@testdomain.tld"], [("", "test@testdomain.tld")], False)
        ])
@patch('Emailkasten.mailParsing.logger')
def test__separateRFC2822MailAddressFormat(mock_logger, testMailers, expectedResult, warningCalled):
    separatedMailers = Emailkasten.mailParsing._separateRFC2822MailAddressFormat(testMailers)
    assert separatedMailers == expectedResult

@patch('Emailkasten.mailParsing.logger')
def test__parseMessageID_success(mock_logger, test_good_mailMessage):
    messageID = Emailkasten.mailParsing._parseMessageID(test_good_mailMessage)
    assert messageID == 'abcdefgäöüß§'
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()

@patch('Emailkasten.mailParsing.logger')
def test__parseMessageID_emptyMessage(mock_logger, test_bad_mailMessage):
    messageID = Emailkasten.mailParsing._parseMessageID(test_bad_mailMessage)
    assert messageID == str(hash(test_bad_mailMessage))
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_not_called()

@pytest.mark.xfail
@patch('Emailkasten.mailParsing.logger')
def test__parseMessageID_noMessage(mock_logger, test_no_mailMessage):
    messageID = Emailkasten.mailParsing._parseMessageID(test_no_mailMessage)


@patch('Emailkasten.mailParsing.logger')
def test__parseDate_success(mock_logger, test_good_mailMessage):
    date = Emailkasten.mailParsing._parseDate(test_good_mailMessage)
    assert date == datetime.datetime(2001, 11, 9, 1, 8, 47)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()

@patch('Emailkasten.mailParsing.logger')
def test__parseDate_emptyMessage(mock_logger, test_bad_mailMessage):
    date = Emailkasten.mailParsing._parseDate(test_bad_mailMessage)
    assert date == datetime.datetime(1971, 1, 1, 0, 0, 0)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_not_called()

@pytest.mark.xfail
@patch('Emailkasten.mailParsing.logger')
def test__parseDate_noMessage(mock_logger, test_no_mailMessage):
    date = Emailkasten.mailParsing._parseDate(test_no_mailMessage)


@pytest.mark.parametrize(
    "stripTexts, expectedResult",
    [(True, "This a test SUBJEcT line äöüß§"), (False, "This a test SUBJEcT line äöüß§ \t ")],
)
@patch("Emailkasten.mailParsing.ParsingConfiguration")
@patch("Emailkasten.mailParsing.logger")
def test__parseSubject_success(mock_logger, mock_parsingConfiguration, stripTexts, expectedResult, test_special_mailMessage):
    mock_parsingConfiguration.STRIP_TEXTS = stripTexts
    subject = Emailkasten.mailParsing._parseSubject(test_special_mailMessage)
    assert subject == expectedResult
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()

@patch('Emailkasten.mailParsing.logger')
def test__parseSubject_emptyMessage(mock_logger, test_bad_mailMessage):
    subject = Emailkasten.mailParsing._parseSubject(test_bad_mailMessage)
    assert subject == ''
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_not_called()

@pytest.mark.xfail
@patch('Emailkasten.mailParsing.logger')
def test__parseSubject_noMessage(mock_logger, test_no_mailMessage):
    subject = Emailkasten.mailParsing._parseSubject(test_no_mailMessage)


@patch('Emailkasten.mailParsing.logger')
def test__parseHeader_success(mock_logger, test_good_mailMessage):
    header = Emailkasten.mailParsing._parseHeader(test_good_mailMessage, "test")
    assert header == "test äöüß§"
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()

@patch('Emailkasten.mailParsing.logger')
def test__parseHeader_emptyMessage(mock_logger, test_bad_mailMessage):
    header = Emailkasten.mailParsing._parseHeader(test_bad_mailMessage, "test")
    assert header == ''
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()

@pytest.mark.xfail
@patch('Emailkasten.mailParsing.logger')
def test__parseHeader_noMessage(mock_logger, test_no_mailMessage):
    header = Emailkasten.mailParsing._parseHeader(test_no_mailMessage, "test")


@patch('Emailkasten.mailParsing.logger')
def test__parseMultipleHeader_success(mock_logger, test_good_mailMessage):
    header = Emailkasten.mailParsing._parseMultipleHeader(test_good_mailMessage, "multi")
    assert header == "test\näöüß§\t\n123456"
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()

@patch('Emailkasten.mailParsing.logger')
def test__parseMultipleHeader_emptyMessage(mock_logger, test_bad_mailMessage):
    header = Emailkasten.mailParsing._parseMultipleHeader(test_bad_mailMessage, "multi")
    assert header == ''
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()

@pytest.mark.xfail
@patch('Emailkasten.mailParsing.logger')
def test__parseMultipleHeader_noMessage(mock_logger, test_no_mailMessage):
    header = Emailkasten.mailParsing._parseMultipleHeader(test_no_mailMessage, "multi")
