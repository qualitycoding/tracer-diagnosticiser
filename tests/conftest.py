# FROZEN — DO NOT MODIFY (tests/FROZEN_MANIFEST.sha256)
import datetime as _dt
import pytest
from tests.fixtures.fake_elm import FakeElm, FakeClock


@pytest.fixture
def fake_elm():
    return FakeElm()


@pytest.fixture
def fixed_now():
    return _dt.datetime(2026, 9, 26, 12, 0, 0, tzinfo=_dt.timezone.utc)


@pytest.fixture
def fake_clock():
    return FakeClock()
