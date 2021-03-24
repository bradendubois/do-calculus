from inspect import empty, getmembers, getsource, ismethod, signature, Signature
from os import chdir
from os.path import abspath, dirname
from pathlib import Path

from do.API import Do


def api_docstring_description(function_name):

    def parameter_signature(parameter_item):
        parameter_key, parameter_value = parameter_item
        return f"- **{parameter_key}** ```py\n{parameter_value.annotation}\n```"

    name = str(function_name.__name__)

    function_signature = f"## Function Signature - {signature(function_name, follow_wrapped=True)}\n"

    source = getsource(function_name)
    header = source.split("\n")[0][:-1].split(" ", maxsplit=1)[1].strip(" ")
    header = f"### Return Value\n\n```py\n{header}\n```\n"
    
    parameters = "\n".join(map(parameter_signature, function_signature.parameters.items()))
    if len(parameters) == 0:
        parameters =  "### Parameters\n\n**None**\n"
    
    if function_signature.return_annotation is not Signature.smpty:
        return_annotation = function_signature.return_annotation
    else:
        return_annotation = "None"

    return_value = f"### Return Value\n\n```py\n{return_annotation}\n```\n"
    
    sections = [signature, header, parameters, return_value]
    
    return "\n".join(sections)


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
