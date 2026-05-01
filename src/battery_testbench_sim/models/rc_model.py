class RCModel:
    def __init__(self, R: float = 0.8, C: float = 10.0):
        self.R = R
        self.C = C
        self.v_rc = 0.0

    def step(self, current: float, dt: float) -> float:
        tau = self.R * self.C

        target_v = current * self.R
        dv = (target_v - self.v_rc) / tau * dt

        self.v_rc += dv
        return self.v_rc