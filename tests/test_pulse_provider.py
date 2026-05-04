import pytest

from battery_testbench_sim.providers.pulse_provider import PulseBMSDataProvider


def test_pulse_provider_generates_rest_pulse_rest_sequence():
    provider = PulseBMSDataProvider(
        soc=50,
        pre_rest_cycles=2,
        pulse_current=-5.0,
        pulse_cycles=3,
        post_rest_cycles=2,
        pack_voltage=300.0,
        state=1,
        fault_level=0,
    )

    values = [provider.get_status_data() for _ in range(7)]

    currents = [item["pack_current"] for item in values]
    socs = [item["soc"] for item in values]

    assert currents == [
        0.0,
        0.0,
        -5.0,
        -5.0,
        -5.0,
        0.0,
        0.0,
    ]

    assert socs == [50, 50, 50, 50, 50, 50, 50]

    with pytest.raises(StopIteration, match="Scenario completed"):
        provider.get_status_data()


def test_pulse_provider_rejects_negative_pre_rest_cycles():
    with pytest.raises(ValueError, match="pre_rest_cycles must be non-negative"):
        PulseBMSDataProvider(
            soc=50,
            pre_rest_cycles=-1,
            pulse_current=-5.0,
            pulse_cycles=3,
            post_rest_cycles=2,
            pack_voltage=300.0,
            state=1,
            fault_level=0,
        )


def test_pulse_provider_rejects_non_positive_pulse_cycles():
    with pytest.raises(ValueError, match="pulse_cycles must be positive"):
        PulseBMSDataProvider(
            soc=50,
            pre_rest_cycles=1,
            pulse_current=-5.0,
            pulse_cycles=0,
            post_rest_cycles=2,
            pack_voltage=300.0,
            state=1,
            fault_level=0,
        )


def test_pulse_provider_rejects_negative_post_rest_cycles():
    with pytest.raises(ValueError, match="post_rest_cycles must be non-negative"):
        PulseBMSDataProvider(
            soc=50,
            pre_rest_cycles=1,
            pulse_current=-5.0,
            pulse_cycles=3,
            post_rest_cycles=-1,
            pack_voltage=300.0,
            state=1,
            fault_level=0,
        )