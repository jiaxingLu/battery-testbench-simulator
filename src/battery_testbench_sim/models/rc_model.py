class RCModel:
    def __init__(self, R: float = 0.5, C: float = 20.0):
        self.R = R
        self.C = C
        self.v_rc = 0.0

    def step(self, current: float, dt: float) -> float:
        tau = self.R * self.C

        # I < 0 means discharge, so load_current > 0
        load_current = max(0.0, -current)

        dv = (-self.v_rc + load_current * self.R) / tau * dt
        self.v_rc += dv

        return self.v_rc