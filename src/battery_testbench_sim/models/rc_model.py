class RCModel:
    def __init__(self, R: float = 0.05, C: float = 200.0):
        self.R = R
        self.C = C
        self.v_rc = 0.0

    def step(self, current: float, dt: float) -> float:
        tau = self.R * self.C

        # Convention:
        # current < 0  => discharge
        # v_rc > 0    => polarization voltage drop
        load_current = max(0.0, -current)

        dv = (-self.v_rc + load_current * self.R) / tau * dt
        self.v_rc += dv

        return self.v_rc