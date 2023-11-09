from pyflowlauncher.result import Result


def test_asdict():
    r = Result(
        Title="Test",
        SubTitle="Test",
        IcoPath="Test.png",
        ContextData=["Test"],
        Glyph={"Glyph": "Test", "FontFamily": "Test"},
        CopyText="Test",
        AutoCompleteText="Test",
        RoundedIcon=True,
        JsonRPCAction={
            "Method": "Test",
            "Parameters": ["Test"],
            "DontHideAfterAction": True
        }
    )
    assert r.as_dict() == {
        "Title": "Test",
        "SubTitle": "Test",
        "IcoPath": "Test.png",
        "Score": 0,
        "JsonRPCAction": {
            "Method": "Test",
            "Parameters": ["Test"],
            "DontHideAfterAction": True
        },
        "ContextData": ["Test"],
        "Glyph": {
            "Glyph": "Test",
            "FontFamily": "Test"
        },
        "CopyText": "Test",
        "AutoCompleteText": "Test",
        "RoundedIcon": True
    }


def test_add_action():
    r = Result(
        Title="Test"
    )
    r.add_action(lambda: None, ["Test"], dont_hide_after_action=True)
    assert r.JsonRPCAction == {
        "Method": "<lambda>",
        "Parameters": ["Test"],
        "DontHideAfterAction": True
    }
