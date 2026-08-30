import asyncio

import pytest
from pyflowlauncher.plugin import Plugin
from pyflowlauncher.launcher import Launcher
from pyflowlauncher.result import Result, send_results


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


def _trigger_context_menu(plugin, context_data):
    return asyncio.run(plugin._event_handler.trigger_event('context_menu', context_data))


def test_default_context_menu_is_registered():
    plugin = Plugin()
    assert 'context_menu' in plugin._event_handler._events


def test_default_context_menu_rebuilds_results_from_wire_dicts():
    plugin = Plugin()
    context_data = [Result(title='menu item', subtitle='sub').to_json()]
    response = _trigger_context_menu(plugin, context_data)
    assert response == send_results([Result(title='menu item', subtitle='sub')])


def test_default_context_menu_accepts_result_instances():
    plugin = Plugin()
    menu = Result(title='menu item')
    assert _trigger_context_menu(plugin, [menu]) == send_results([menu])
    assert _trigger_context_menu(plugin, menu) == send_results([menu])


def test_default_context_menu_skips_non_result_items():
    plugin = Plugin()
    response = _trigger_context_menu(plugin, ['token', 42, {'no': 'title'}])
    assert response == send_results([])


def test_default_context_menu_handles_non_iterable_data():
    plugin = Plugin()
    assert _trigger_context_menu(plugin, None) is None
    assert _trigger_context_menu(plugin, 'token') is None


def test_user_context_menu_overrides_default():
    plugin = Plugin()

    @plugin.on_method
    def context_menu(data):
        return Result(title='custom')

    response = _trigger_context_menu(plugin, [Result(title='ignored').to_json()])
    assert response == send_results([Result(title='custom')])


def test_init_methods_context_menu_overrides_default():
    def context_menu(data):
        return Result(title='custom')

    plugin = Plugin(methods=[context_menu])
    response = _trigger_context_menu(plugin, ['anything'])
    assert response == send_results([Result(title='custom')])


def test_exception_handler():
    plugin = Plugin()

    @plugin.on_except(KeyError)
    def action(e: Exception):
        print('OH NO!')
        return {'result': [{'title': 'title', 'subtitle': 'subtitle', 'icon': 'icon.png'}]}

    assert plugin._event_handler._handlers == {KeyError: action}
