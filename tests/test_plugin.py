from pyflowlauncher.plugin import Plugin


def temp_method1():
    return None


def temp_method2():
    return None


def query(query: str):
    return {'result': [{'title': 'title', 'subtitle': 'subtitle', 'icon': 'icon.png'}]}


def test_add_method():
    plugin = Plugin()
    plugin.add_method(temp_method1)
    assert plugin._event_handler._methods == {'temp_method1': temp_method1}


def test_add_methods():
    plugin = Plugin()
    plugin.add_methods([temp_method1, temp_method2])
    assert plugin._event_handler._methods == {'temp_method1': temp_method1, 'temp_method2': temp_method2}


def test_settings():
    plugin = Plugin()
    plugin._client.recieve = lambda: {'method': 'settings', 'parameters': [], 'settings': {'test': 'test'}}
    assert plugin.settings == {'test': 'test'}