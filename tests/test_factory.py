from quizzz import create_app


def test_config():
    """
    If config is not passed, there should be some default configuration,
    otherwise the configuration should be overridden.
    """
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_index(client):
    response = client.get('/')
    assert b'Home' in response.data
