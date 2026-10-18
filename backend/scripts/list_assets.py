from cyberwave import Cyberwave

cw = Cyberwave()
try:
    assets = cw.assets.list()
    print(f"{len(assets)} assets\n")
    for a in sorted(assets, key=lambda a: bool(a.fixed_base)):
        mobile = "MOBILE" if not a.fixed_base else "fixed "
        caps = sorted((a.capabilities or {}).keys())
        print(f"{mobile} | {a.registry_id or a.slug} | {a.name} | "
              f"sim={a.supported_simulation_backends} | caps={caps}")
finally:
    cw.disconnect()
