from pyflowlauncher.result import Result


def test_asdict():
    r = Result(
        title="Test",
        subtitle="Test",
        icon="Test.png",
        title_highlight_data=[0],
        context_data=["Test"],
        glyph={"Glyph": "Test", "FontFamily": "Test"},
        copy_text="Test",
        auto_complete_text="Test",
        rounded_icon=True,
        json_rpc_action={
            "Method": "Test",
            "Parameters": ["Test"],
            "DontHideAfterAction": True
        },
        preview={
            "PreviewImagePath": "Test.png",
            "Description": "Test",
            "IsMedia": True,
            "PreviewDeligate": None
        }
    )
    assert r.as_dict() == {
        "title": "Test",
        "subtitle": "Test",
        "icon": "Test.png",
        "title_highlight_data": [0],
        "score": 0,
        "json_rpc_action": {
            "Method": "Test",
            "Parameters": ["Test"],
            "DontHideAfterAction": True
        },
        "context_data": ["Test"],
        "glyph": {
            "Glyph": "Test",
            "FontFamily": "Test"
        },
        "copy_text": "Test",
        "auto_complete_text": "Test",
        "rounded_icon": True,
        "preview": {
            "PreviewImagePath": "Test.png",
            "Description": "Test",
            "IsMedia": True,
            "PreviewDeligate": None
        }
    }


def test_add_action():
    r = Result(title="Test")
    method = lambda: None
    method._is_registered_method = True
    r.add_action(method, ["Test"], dont_hide_after_action=True)
    assert r.json_rpc_action == {
        "Method": "<lambda>",
        "Parameters": ["Test"],
        "DontHideAfterAction": True
    }


def test_add_action_return():
    r = Result(title="Test").add_action(lambda: None)
    assert isinstance(r, Result)
