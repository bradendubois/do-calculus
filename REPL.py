
# TODO - fake stubs, would use functions in /api and direct API functions
foo = lambda x: x
foo1 = lambda x: x
foo2 = lambda x: x
load_model = lambda x: x
list_graphs = lambda x: x
paths = lambda x: x

function_map = {
    (list_graphs, foo): ["list", "all", "see"],
    (load_model, foo): ["load", "start", "graph"],
    (foo1, foo): ["probability", "p", "compute", "query"],
    (foo2, foo): ["dcs", "dcf", "deconfound", "deconfounding"],
    (paths, foo): ["backdoor"]
}

exit_options = ["quit", "exit", "stop", "leave", "q"]

assert len(set().union(*function_map.values())) == sum(map(len, function_map.values())), \
    "Conflicting keywords; one input maps to more than two possible options!"

lookup = dict()
for f, v in function_map.items():
    lookup.update({k: f for k in v})

data = cg = None

while user_str := input(">> ").strip().split(" ", 1):

    f, args = user_str[0].lower(), user_str[1:]

    if f in exit_options:
        break

    if f not in lookup:
        print("Error; input not in options. Try 'help' or '?' for options.")
        continue

    parse, func = lookup[f]

    print(func(parse(args)))
