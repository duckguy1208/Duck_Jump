def clamp(n, min_val, max_val):
    return max(min(n, max_val), min_val)


def clamp_platform_distance(n):
    return clamp(n, 0, 290)
