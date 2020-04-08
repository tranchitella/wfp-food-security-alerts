import os

from wfp_food_security_alerts import config


def test_config(tmpdir):
    filename = os.path.join(tmpdir, 'config.yaml')
    with open(filename, 'wb') as f:
        f.write(b"test: 1\n")
    data = config.read_config_file(filename)
    assert data == {'test': 1}
    os.unlink(filename)


def test_config_not_found():
    data = config.read_config_file("/does/not/exist")
    assert data is None


def test_config_invalid_yaml(tmpdir):
    filename = os.path.join(tmpdir, 'config.yaml')
    with open(filename, 'wb') as f:
        f.write(b"a: b: 1\n")
    data = config.read_config_file(filename)
    assert data is None
