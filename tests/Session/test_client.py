import inspect
import os

from unittest.mock import patch, ANY
from AwAws.Session.session import Session


def test_session():
    session = Session()
    assert session.session is None
    assert session.region_name is None
    assert session.role_arn is None
    inspect.isclass(Session)
    assert isinstance(session, Session)


def test_init_with_role_and_region():
    test_region_name = 'us-least-5'
    test_role_arn = 'arn:aws:iam::111111111:role/net.dilex.some.test.role'
    session = Session(role_arn=test_role_arn, region_name=test_region_name)
    assert session.role_arn == 'arn:aws:iam::111111111:role/net.dilex.some.test.role'
    assert session.region_name == 'us-least-5'


def test_init_with_role_none():
    test_role_arn = None
    session = Session(role_arn=test_role_arn)
    assert session.role_arn is None


def test_session_region():
    session = Session(region_name='us-least-9')
    assert session.region_name == 'us-least-9'


def test_set_region():
    session = Session()
    session.set_region('us-least-8')
    assert session.region_name == 'us-least-8'


def test_get_region():
    session = Session()
    session.set_region(region_name='us-least-6')
    assert session.region_name == 'us-least-6'
    assert session.get_region() == 'us-least-6'


def test_session_region_env():
    session = Session()
    assert session.get_region() is None

    os.environ['AWS_REGION'] = 'us-least-7'
    session.set_region()
    assert session.region_name == 'us-least-7'
    assert session.get_region() == 'us-least-7'
    os.environ.pop('AWS_REGION')


@patch('botocore.session.Session.create_client', autospec=True, return_value='boto!')
@patch('AwAws.Session.sts.Sts.assume_role', autospec=True, return_value=None)
def test_client_with_service(sts, cc):
    session = Session()
    chk = session.get_client('project-grand-slam')
    assert chk == 'boto!'
    cc.assert_called_with(
        ANY,
        'project-grand-slam',
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
        region_name=None
    )
    sts.assert_not_called()


@patch('botocore.session.Session.create_client', autospec=True, return_value='boto!')
@patch('AwAws.Session.session.Sts')
def test_get_client_with_role(sts, cc):

    sts.assume_role.return_value = 20
    sts().aws_access_key_id = 'my_access_key'
    sts().aws_secret_access_key = 'my_secret_key'
    sts().aws_session_token = 'my_session_token'

    test_role_arn = 'arn:aws:iam::111111111:role/net.dilex.some.test.role'
    session = Session(role_arn=test_role_arn)
    chk = session.get_client('project-grand-slam')

    assert chk == 'boto!'
    cc.assert_called_once()
    cc.assert_called_with(
        ANY,
        'project-grand-slam',
        aws_access_key_id='my_access_key',
        aws_secret_access_key='my_secret_key',
        aws_session_token='my_session_token',
        region_name=None
    )


