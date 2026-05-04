from battery_testbench_sim.runtime import supervisor as supervisor_module
from battery_testbench_sim.runtime.supervisor import Supervisor


class DummyBMS:
    cycle_time_s = 0.5


class DummyVerifier:
    pass


class DummyBus:
    pass


class DummyFaultInjector:
    pass


def make_supervisor(sleep_enabled: bool) -> Supervisor:
    return Supervisor(
        bms=DummyBMS(),
        verifier=DummyVerifier(),
        bus_tx=DummyBus(),
        bus_rx=DummyBus(),
        fault_injector=DummyFaultInjector(),
        bms_status_id=0x100,
        raw_trace_enabled=False,
        sleep_enabled=sleep_enabled,
    )


def test_sleep_if_enabled_calls_time_sleep(monkeypatch):
    calls = []

    def fake_sleep(seconds):
        calls.append(seconds)

    monkeypatch.setattr(supervisor_module.time, "sleep", fake_sleep)

    supervisor = make_supervisor(sleep_enabled=True)
    supervisor._sleep_if_enabled()

    assert calls == [0.5]


def test_sleep_if_disabled_skips_time_sleep(monkeypatch):
    calls = []

    def fake_sleep(seconds):
        calls.append(seconds)

    monkeypatch.setattr(supervisor_module.time, "sleep", fake_sleep)

    supervisor = make_supervisor(sleep_enabled=False)
    supervisor._sleep_if_enabled()

    assert calls == []

def test_max_cycles_disabled_by_default():
    supervisor = make_supervisor(sleep_enabled=False)

    supervisor.cycle_count = 10

    assert supervisor._max_cycles_reached() is False


def test_max_cycles_not_reached_before_limit():
    supervisor = make_supervisor(sleep_enabled=False)
    supervisor.max_cycles = 5

    supervisor.cycle_count = 4

    assert supervisor._max_cycles_reached() is False


def test_max_cycles_reached_at_limit():
    supervisor = make_supervisor(sleep_enabled=False)
    supervisor.max_cycles = 5

    supervisor.cycle_count = 5

    assert supervisor._max_cycles_reached() is True


def test_max_cycles_rejects_negative_value():
    try:
        Supervisor(
            bms=DummyBMS(),
            verifier=DummyVerifier(),
            bus_tx=DummyBus(),
            bus_rx=DummyBus(),
            fault_injector=DummyFaultInjector(),
            bms_status_id=0x100,
            raw_trace_enabled=False,
            sleep_enabled=False,
            max_cycles=-1,
        )
    except ValueError as exc:
        assert "max_cycles must be non-negative" in str(exc)
    else:
        raise AssertionError("Expected ValueError for negative max_cycles.")    