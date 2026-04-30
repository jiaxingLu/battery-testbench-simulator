from battery_testbench_sim.faults.fault_injector import FaultInjector


def test_fault_injector_does_nothing_when_disabled():
    injector = FaultInjector({"enabled": False})
    data = {"soc": 30, "fault_level": 0}

    result = injector.apply(data, cycle_count=10)

    assert result == data


def test_fault_injector_waits_until_trigger_cycle():
    injector = FaultInjector({
        "enabled": True,
        "trigger_after_cycles": 5,
        "fault_level": 2,
        "soc_override": 5,
    })
    data = {"soc": 30, "fault_level": 0}

    result = injector.apply(data, cycle_count=4)

    assert result["soc"] == 30
    assert result["fault_level"] == 0


def test_fault_injector_applies_after_trigger_cycle():
    injector = FaultInjector({
        "enabled": True,
        "trigger_after_cycles": 5,
        "fault_level": 2,
        "soc_override": 5,
    })
    data = {"soc": 30, "fault_level": 0}

    result = injector.apply(data, cycle_count=5)

    assert result["soc"] == 5
    assert result["fault_level"] == 2