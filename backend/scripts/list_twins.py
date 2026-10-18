from cyberwave import Cyberwave

cw = Cyberwave()
try:
    for t in cw.twins.list():
        print(t.uuid, "|", t.name, "|", getattr(t, "environment_uuid", None))
finally:
    cw.disconnect()
