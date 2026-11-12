import json
import logging

import pytest

from pyflowlauncher.launcher import FlowLauncherV1, FlowLauncherV2
from pyflowlauncher.manifest import Manifest
from pyflowlauncher.plugin import Plugin

FULL_MANIFEST = {
    'ID': 'abc',
    'Name': 'Test',
    'Author': 'me',
    'Version': '1.0.0',
    'Language': 'python_v2',
    'Description': 'desc',
    'Website': 'https://example.com',
    'ExecuteFileName': 'main.py',
    'IcoPath': 'icon.png',
    'ActionKeyword': 'tp',
}


@pytest.fixture
def plugin_dir(tmp_path, monkeypatch):
    monkeypatch.setattr('sys.argv', [str(tmp_path / 'main.py')])
    # The package logger doesn't propagate (it writes to plugin.log);
    # pytest < 9 caplog only sees propagated records.
    monkeypatch.setattr(logging.getLogger('pyflowlauncher'), 'propagate', True)
    return tmp_path


def manifest_warnings(caplog):
    return [r for r in caplog.records
            if r.levelno == logging.WARNING and 'manifest' in r.getMessage().lower()]


def write_manifest(plugin_dir, data):
    (plugin_dir / 'plugin.json').write_text(json.dumps(data), encoding='utf-8')


class TestDetectionReadsOnlyLanguage:

    def test_v2_without_action_keyword(self, plugin_dir):
        write_manifest(plugin_dir, {'Language': 'python_v2', 'ActionKeywords': ['tp']})
        assert isinstance(Plugin()._launcher, FlowLauncherV2)

    def test_v2_with_only_language(self, plugin_dir):
        write_manifest(plugin_dir, {'Language': 'python_v2'})
        assert isinstance(Plugin()._launcher, FlowLauncherV2)

    def test_v2_language_is_case_insensitive(self, plugin_dir):
        write_manifest(plugin_dir, {'Language': 'Python_V2'})
        assert isinstance(Plugin()._launcher, FlowLauncherV2)

    def test_python_is_v1(self, plugin_dir):
        write_manifest(plugin_dir, {'Language': 'python'})
        assert isinstance(Plugin()._launcher, FlowLauncherV1)

    def test_missing_manifest_is_v1_without_warning(self, plugin_dir, caplog):
        with caplog.at_level(logging.WARNING):
            plugin = Plugin()
        assert isinstance(plugin._launcher, FlowLauncherV1)
        assert manifest_warnings(caplog) == []

    def test_unreadable_json_warns_and_is_v1(self, plugin_dir, caplog):
        (plugin_dir / 'plugin.json').write_text('{not json', encoding='utf-8')
        with caplog.at_level(logging.WARNING):
            plugin = Plugin()
        assert isinstance(plugin._launcher, FlowLauncherV1)
        assert manifest_warnings(caplog)

    def test_missing_language_warns_and_is_v1(self, plugin_dir, caplog):
        write_manifest(plugin_dir, {'ActionKeywords': ['tp']})
        with caplog.at_level(logging.WARNING):
            plugin = Plugin()
        assert isinstance(plugin._launcher, FlowLauncherV1)
        assert manifest_warnings(caplog)


class TestManifestActionKeywords:

    def test_keywords_without_keyword(self):
        data = {**FULL_MANIFEST, 'ActionKeywords': ['tp', 'test']}
        del data['ActionKeyword']
        manifest = Manifest.from_json(data)
        assert manifest.action_keyword == 'tp'
        assert manifest.action_keywords == ['tp', 'test']

    def test_keyword_without_keywords(self):
        manifest = Manifest.from_json(FULL_MANIFEST)
        assert manifest.action_keyword == 'tp'
        assert manifest.action_keywords == ['tp']

    def test_both_present_are_kept(self):
        data = {**FULL_MANIFEST, 'ActionKeyword': 'a', 'ActionKeywords': ['b', 'c']}
        manifest = Manifest.from_json(data)
        assert manifest.action_keyword == 'a'
        assert manifest.action_keywords == ['b', 'c']

    def test_neither_is_still_an_error(self):
        data = dict(FULL_MANIFEST)
        del data['ActionKeyword']
        with pytest.raises(KeyError):
            Manifest.from_json(data)

    def test_empty_keywords_without_keyword_is_an_error(self):
        data = {**FULL_MANIFEST, 'ActionKeywords': []}
        del data['ActionKeyword']
        with pytest.raises(KeyError):
            Manifest.from_json(data)

    def test_other_required_keys_are_unchanged(self):
        data = dict(FULL_MANIFEST)
        del data['Website']
        with pytest.raises(KeyError):
            Manifest.from_json(data)
