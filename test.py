from do.API import API
from pathlib import Path
from do.core.Expression import Expression
from do.core.Model import from_yaml
from do.core.Variables import Intervention, Outcome

a = API()

p = "./models/pearl-3.4.yml"
m = from_yaml(p)

paths = a.backdoors({"X1"}, {"Xj"}, m.graph())
print(paths)


paths = a.backdoors({"Xj"}, {"X1"}, m.graph())
print(paths)

print(a.treat(Expression(Outcome("Xj", "xj")), [Intervention("X1", "x1")], m))
