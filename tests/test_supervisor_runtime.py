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