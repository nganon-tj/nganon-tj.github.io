import os
import pytest

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data',
    )

def f_datadir(path):
    return os.path.join(FIXTURE_DIR, path)

@pytest.fixture
def datafile():
    return f_datadir