from battery_testbench_sim.providers.scenario_provider import ScenarioBMSDataProvider


def test_scenario_provider_decreases_soc_by_configured_step():
    provider = ScenarioBMSDataProvider(
        start_soc=30,
        end_soc=5,
        soc_step_per_cycle=5,
        pack_voltage_start=330.0,
        pack_voltage_end=300.0,
        pack_current=-5.0,
        state=1,
        fault_level=0,
    )

    data_0 = provider.get_status_data()
    data_1 = provider.get_status_data()
    data_2 = provider.get_status_data()

    assert data_0["soc"] == 30
    assert data_1["soc"] == 25
    assert data_2["soc"] == 20


def test_scenario_provider_clamps_soc_at_end_soc():
    provider = ScenarioBMSDataProvider(
        start_soc=10,
        end_soc=5,
        soc_step_per_cycle=3,
        pack_voltage_start=310.0,
        pack_voltage_end=300.0,
        pack_current=-5.0,
        state=1,
        fault_level=0,
    )

    values = [provider.get_status_data()["soc"] for _ in range(5)]

    assert values == [10, 7, 5, 5, 5]


def test_scenario_provider_interpolates_voltage():
    provider = ScenarioBMSDataProvider(
        start_soc=30,
        end_soc=10,
        soc_step_per_cycle=10,
        pack_voltage_start=330.0,
        pack_voltage_end=300.0,
        pack_current=-5.0,
        state=1,
        fault_level=0,
    )

    data_0 = provider.get_status_data()
    data_1 = provider.get_status_data()
    data_2 = provider.get_status_data()

    assert data_0["soc"] == 30
    assert data_1["soc"] == 20
    assert data_2["soc"] == 10


def test_scenario_provider_stops_after_configured_rest_cycles():
    provider = ScenarioBMSDataProvider(
        start_soc=3,
        end_soc=0,
        soc_step_per_cycle=1,
        pack_voltage_start=300.0,
        pack_voltage_end=280.0,
        pack_current=-5.0,
        state=1,
        fault_level=0,
        rest_cycles_after_end=2,
    )

    data_0 = provider.get_status_data()
    data_1 = provider.get_status_data()
    data_2 = provider.get_status_data()
    data_3 = provider.get_status_data()
    data_4 = provider.get_status_data()

    assert data_0["soc"] == 3
    assert data_0["pack_current"] == -5.0

    assert data_1["soc"] == 2
    assert data_1["pack_current"] == -5.0

    assert data_2["soc"] == 1
    assert data_2["pack_current"] == -5.0

    assert data_3["soc"] == 0
    assert data_3["pack_current"] == 0.0

    assert data_4["soc"] == 0
    assert data_4["pack_current"] == 0.0

    try:
        provider.get_status_data()
    except StopIteration as exc:
        assert "Scenario completed" in str(exc)
    else:
        raise AssertionError("Expected StopIteration after configured rest cycles.")