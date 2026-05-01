from __future__ import annotations


def ocv_from_soc(soc: float) -> float:
    """
    简单 OCV 曲线（带平台区）
    SOC: 0–100（这里你用 5–30 区间也适用）
    返回：电压（V）
    """

    # 归一化到 0–1
    s = max(0.0, min(1.0, (soc - 5) / (30 - 5)))

    # 分段近似（模仿 Li-ion 曲线）
    if s < 0.1:
        # 低 SOC 区（陡降）
        return 3.0 + 2.0 * s
    elif s < 0.9:
        # 平台区（缓变）
        return 3.2 + 0.4 * (s - 0.1) / 0.8
    else:
        # 高 SOC 区（抬升）
        return 3.6 + 0.6 * (s - 0.9) / 0.1