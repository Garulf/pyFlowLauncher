import pytest
from pyflowlauncher.plugin import Plugin
from pyflowlauncher.launcher import Launcher


def temp_method1():
    return None


def temp_method2():
    return None


def query(query: str):
    return {'result': [{'title': 'title', 'subtitle': 'subtitle', 'icon': 'icon.png'}]}


def test_add_method():
    plugin = Plugin()
    plugin.add_method(temp_method1)
    assert 'temp_method1' in plugin._event_handler._events


def test_add_methods():
    plugin = Plugin()
    plugin.add_methods([temp_method1, temp_method2])
    assert 'temp_method1' in plugin._event_handler._events
    assert 'temp_method2' in plugin._event_handler._events


def test_settings():
    class MockLauncher(Launcher):
        @property
        def settings(self):
            return {'test': 'test'}
        async def run(self, dispatch):
            pass

    plugin = Plugin(launcher=MockLauncher())
    assert plugin.settings == {'test': 'test'}


def test_run_dir(tmp_path, monkeypatch):
    monkeypatch.setattr('sys.argv', [tmp_path / 'plugin.py'])
    plugin = Plugin()
    assert plugin.run_dir == tmp_path


def test_root_dir(tmp_path, monkeypatch):
    monkeypatch.setattr('sys.argv', [tmp_path / 'plugin.py'])
    monkeypatch.setattr('pyflowlauncher.plugin.Path.exists', lambda _: True)
    plugin = Plugin()
    assert plugin.root_dir == tmp_path


def test_root_dir_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr('sys.argv', [tmp_path / 'plugin.py'])
    monkeypatch.setattr('pyflowlauncher.plugin.Path.exists', lambda _: False)
    plugin = Plugin()
    with pytest.raises(FileNotFoundError):
        assert plugin.root_dir == tmp_path


def test_action():
    plugin = Plugin()
    action = plugin.action(query)
    assert action == {'method': 'query', 'parameters': []}


def test_exception_handler():
    plugin = Plugin()

    @plugin.on_except(KeyError)
    def action(e: Exception):
        print('OH NO!')
        return {'result': [{'title': 'title', 'subtitle': 'subtitle', 'icon': 'icon.png'}]}

    assert plugin._event_handler._handlers == {KeyError: action}
