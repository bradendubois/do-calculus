from pathlib import Path

from do.API import API
from do.core.Inference import validate
from do.core.Model import from_path


api = API()

# directory of YML files containing valid models for testing purposes
model_path = Path("models")
assert model_path.is_dir()

models = dict()
for file in model_path.iterdir():
    models[file.name] = from_path(file)

# verify all the models as correct
#for name, model in models.items():
#    assert validate(model)
