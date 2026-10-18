import math
import time

from cyberwave import Cyberwave

cw = Cyberwave()
try:
    cw.affect("sim", environment_id="8fa26b4e-6395-499f-96d3-1860d463413a", duration=60)

    robot = cw.twin(twin_id="03a3e4d0-1c23-4b2c-afd7-fa5389bd755e")   # reuse: policy already attached


    view = robot.pose.get(timeout=5.0)        # LIVE view: updates in place
    before = view.translation_dict()          # snapshot NOW as a plain dict
    print("before:", before)
    if before is None:
        print("no pose yet; sending one move to trigger publishing")
        robot.locomotion.move_forward(0.3, duration=0.5, rate_hz=10)
        time.sleep(2.0)
        before = view.translation_dict()
        print("before (after nudge):", before)
        if before is None:
            raise SystemExit("Still no pose: record as finding, use mock adapter")


    robot.locomotion.move_forward(0.3, duration=1.0, rate_hz=10)
    time.sleep(1.5)                           # pose arrives async over MQTT

    after = view.translation_dict()           # same view, new snapshot
    print("after: ", after)

    dist = math.hypot(after["x"] - before["x"], after["y"] - before["y"])
    print(f"displacement: {dist:.3f} m")
    assert dist > 0.05, f"Robot did not move (displacement {dist:.3f} m)"
    print("PROOF OK: commanded move, verified by pose readback")
finally:
    cw.disconnect()
