from cyberwave import Cyberwave

TWIN_ID = "03a3e4d0-1c23-4b2c-afd7-fa5389bd755e"

def stored_xy(cw: Cyberwave) -> tuple[float, float]:
    data = cw.twins.get_raw(TWIN_ID)
    get = (lambda k: data[k]) if isinstance(data, dict) else (lambda k: getattr(data, k))
    return float(get("position_x")), float(get("position_y"))

cw = Cyberwave()
try:
    robot = cw.twin(twin_id=TWIN_ID)
    print("before:", stored_xy(cw))
    target = (1.5, -0.5)
    robot.edit_position(x=target[0], y=target[1], z=0.0)
    after = stored_xy(cw)
    print("after: ", after)
    assert abs(after[0] - target[0]) < 1e-3 and abs(after[1] - target[1]) < 1e-3, "position not persisted"
    print("PROOF OK: commanded reposition, verified by independent readback")
finally:
    cw.disconnect()
