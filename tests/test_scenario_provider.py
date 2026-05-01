from battery_testbench_sim.providers.scenario_provider import ScenarioBMSDataProvider


def test_scenario_provider_decreases_soc_per_cycle():
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

    assert data_0["pack_voltage"] == 330.0
    assert data_1["pack_voltage"] == 315.0
    assert data_2["pack_voltage"] == 300.0