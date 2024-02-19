from pyflowlauncher.jsonrpc import id_generation


def test_increment_int():
    id_gen = id_generation.incremental_int(1)
    assert next(id_gen) == 1
    assert next(id_gen) == 2
