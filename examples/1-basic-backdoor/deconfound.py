from pathlib import Path

from do import API, Expression, Intervention, Outcome

api = API()

file = Path("pearl-3.4.yml")
model = api.instantiate_model(file)

xj = Outcome("Xj", "xj")
xi = Intervention("Xi", "xi")
e = Expression(xj, [xi])

# basic inference won't work!
try:
    api.probability(e, model)
    print("This cannot happen!")

except Exception:
    e2 = Expression(xj)
    result = api.treat(e2, [xi], model)
    print(result)
