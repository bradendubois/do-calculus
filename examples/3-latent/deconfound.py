from pathlib import Path

from do import API, Expression, Intervention, Outcome

api = API()

file = Path("3.4-latent.yml")
model = api.instantiate_model(file)

xj = Outcome("Xj", "xj")
xi = Intervention("Xi", "xi")
e = Expression(xj, [xi])

result, proof = api.identification([xj], [xi], model)
print(result)
print(proof)
