from blackmamba.system import Pythonista, PYTHONISTA

if PYTHONISTA:
    from blackmamba.framework.security import (
        set_password, get_password, get_services, delete_password
    )


@Pythonista()
def test_delete_password():
    set_password('s', 'a', 'password')
    assert (get_password('s', 'a') == 'password')
    delete_password('s', 'a')
    assert (get_password('s', 'a') is None)


@Pythonista()
def test_pythonista_compatibility_delete_password_does_not_raise():
    delete_password('s', 'a')
    delete_password('s', 'a')


@Pythonista()
def test_set_password():
    delete_password('s', 'a')
    assert (get_password('s', 'a') is None)
    set_password('s', 'a', 'password')
    assert (get_password('s', 'a') == 'password')
    delete_password('s', 'a')


@Pythonista()
def test_pythonista_compatibility_set_password_does_not_raise():
    set_password('s', 'a', 'password')
    set_password('s', 'a', 'password2')
    delete_password('s', 'a')


@Pythonista()
def test_get_password():
    set_password('s', 'a', 'password')
    assert (get_password('s', 'a') == 'password')
    delete_password('s', 'a')


@Pythonista()
def test_pythonista_compatibility_get_password_does_not_raise():
    delete_password('s', 'a')
    assert (get_password('s', 'a') is None)


@Pythonista()
def test_against_pythonista_keychain():
    import keychain

    set_password('s', 'a', 'password')
    assert (keychain.get_password('s', 'a') == 'password')

    keychain.set_password('s', 'a', 'anotherone')
    assert (get_password('s', 'a') == 'anotherone')

    keychain.delete_password('s', 'a')
    assert (get_password('s', 'a') is None)


@Pythonista()
def test_get_services():
    # We do not want to delete all items in tests -> no test for []

    set_password('s', 'a', 'password')
    set_password('s', 'a2', 'password')

    services = get_services()
    s_services = list(filter(lambda x: x[0] == 's', services))
    assert (len(s_services) == 2)

    s_accounts = sorted([x[1] for x in s_services])
    assert (s_accounts == ['a', 'a2'])

    delete_password('s', 'a')
    delete_password('s', 'a2')

    services = get_services()
    s_services = list(filter(lambda x: x[0] == 's', services))
    assert (len(s_services) == 0)
