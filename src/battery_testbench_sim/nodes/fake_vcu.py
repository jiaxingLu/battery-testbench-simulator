class FakeVCU:
    def __init__(self):
        self.last_state = None

    def process_bms_status(self, data: dict) -> dict:
        soc = data["soc"]

        if soc < 10:
            new_state = 2  # protection
        else:
            new_state = 1  # normal

        self.last_state = new_state

        modified = dict(data)
        modified["state"] = new_state

        return modified