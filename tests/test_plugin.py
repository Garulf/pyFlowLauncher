import pytest
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


def test_run_dir(tmp_path, monkeypatch):
    monkeypatch.setattr('sys.argv', [tmp_path / 'plugin.py'])
    plugin = Plugin()
    assert plugin.plugin_run_dir() == tmp_path


def test_root_dir(tmp_path, monkeypatch):
    monkeypatch.setattr('sys.argv', [tmp_path / 'plugin.py'])
    monkeypatch.setattr('pyflowlauncher.plugin.Path.exists', lambda _: True)
    plugin = Plugin()
    assert plugin.plugin_root_dir() == tmp_path


def test_root_dir_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr('sys.argv', [tmp_path / 'plugin.py'])
    monkeypatch.setattr('pyflowlauncher.plugin.Path.exists', lambda _: False)
    plugin = Plugin()
    with pytest.raises(FileNotFoundError):
        assert plugin.plugin_root_dir() == tmp_path
