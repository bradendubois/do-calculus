from pathlib import Path

from do.core.Model import from_yaml

# directory of YML files containing valid models for testing purposes
model_path = Path("models")
assert model_path.is_dir()

models = dict()
for file in model_path.iterdir():
    models[file.name] = from_yaml(file.absolute())
