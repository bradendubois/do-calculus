from pathlib import Path

from do import API

api = API()

file = Path("pearl-3.4.yml")
model = api.instantiate_model(file)

backdoors = api.backdoors({"Xi"}, {"Xj"}, model.graph())
assert len(backdoors) > 0, "No backdoor paths detected!"
assert not api.blocks({"Xi"}, {"Xj"}, model.graph(), set()), "This should not block all paths!" 

for path in backdoors:
    print("Path:", path)

backdoors = api.backdoors({"Xi"}, {"Xj"}, model.graph(), {"X1", "X4"})
assert len(backdoors) == 0, "Expected this to block!"
assert api.blocks({"Xi"}, {"Xj"}, model.graph(), {"X1", "X4"}), "This should block!"
