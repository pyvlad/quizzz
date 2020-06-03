from quizzz import create_app


def test_config():
    """
    If config is not passed, there should be some default configuration,
    otherwise the configuration should be overridden.
    """
    dev_app = create_app()
    assert not dev_app.testing

    test_app = create_app({'TESTING': True})
    assert test_app.testing


def test_index(client):
    """
    The app should work and the home page should be available.
    """
    response = client.get('/')
    assert b'Home' in response.data
