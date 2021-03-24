from inspect import getmembers, getsource, ismethod, signature
from os import chdir
from os.path import abspath, dirname
from pathlib import Path

from do.API import Do


def api_docstring_description(function_name):

    def parameter_signature(parameter_item):
        parameter_key, parameter_value = parameter_item
        return f"- **{parameter_key}**: ``{parameter_value.annotation}``"

    name = str(function_name.__name__)

    source = getsource(function_name)
    header = source.split("\n")[0][:-1].split(" ", maxsplit=1)[1]
    function_signature = signature(function_name, follow_wrapped=True)

    parameters = "\n".join(map(parameter_signature, function_signature.parameters.items()))

    string = f"## Function Signature - {name}\n\n" \
             f"### Header\n\n```py\n{header}\n```\n\n" \
             f"### Parameters\n\n{parameters}\n" \
             f"### Return Value\n\n```py\n{function_signature.return_annotation}\n```\n"

    return string


def populate_wiki_stubs():

    chdir(dirname(abspath(__file__)))

    api_signatures = {name: api_docstring_description(method) for (name, method) in
                      getmembers(Do(model=None), predicate=ismethod)}

    wiki_dir = Path("pages")

    for file in wiki_dir.iterdir():
        if not file.is_file():
            continue

        text = file.read_text().splitlines()

        found = False
        for line, content in enumerate(text):
            if content.startswith("STUB"):
                stub, function = content.split("|")
                text[line] = api_signatures[function]
                found = True

        if found:
            file.write_text("\n".join(text))


if __name__ == "__main__":
    populate_wiki_stubs()
