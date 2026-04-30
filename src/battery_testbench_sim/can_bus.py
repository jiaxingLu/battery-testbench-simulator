import can


class CanBus:
    def __init__(self, interface: str = "virtual", channel: str = "testbench"):
        self.bus = can.Bus(interface=interface, channel=channel)

    def send(self, arbitration_id: int, data: bytes) -> None:
        msg = can.Message(
            arbitration_id=arbitration_id,
            data=data,
            is_extended_id=False,
        )
        self.bus.send(msg)

    def recv(self, timeout_s: float = 1.0):
        return self.bus.recv(timeout=timeout_s)

    def shutdown(self) -> None:
        self.bus.shutdown()