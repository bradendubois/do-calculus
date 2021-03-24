from inspect import getmembers, getdoc, getsource, isclass, ismethod, signature, Signature
from os import chdir
from os.path import abspath, dirname
from pathlib import Path

from do.API import Do
import do.structures.Exceptions


def api_docstring_description(function_name):

    def parameter_signature(parameter_item):
        parameter_key, parameter_value = parameter_item
        return f"#### {parameter_key}\n```py\n{parameter_value.annotation}\n```"

    name = str(function_name.__name__)
    function_signature = signature(function_name, follow_wrapped=True)

    title = f"## Function Signature - Do.{name}\n"

    source = getsource(function_name)
    header = source.split("\n")[0][:-1].split(" ", maxsplit=1)[1].strip(" ")
    header = f"### Header\n\n```py\n{header}\n```\n"
    
    parameters = "### Parameters\n\n" + "\n".join(map(parameter_signature, function_signature.parameters.items()))
    if len(function_signature.parameters) == 0:
        parameters = "### Parameters\n\n**None**\n"
    
    if function_signature.return_annotation is not Signature.empty:
        return_annotation = function_signature.return_annotation
    else:
        return_annotation = "None"

    return_value = f"### Return Value\n\n```py\n{return_annotation}\n```\n"
    
    sections = [title, header, parameters, return_value]
    
    return "\n".join(sections) + "\n<hr />\n"


def exception_description(exception_name):
    return f"## {exception_name}\n\n> {getdoc(exception_name)}\n\n"


def populate_wiki_stubs():

    chdir(dirname(abspath(__file__)))

    api_signatures = {name: api_docstring_description(method) for (name, method) in
                      getmembers(Do(model=None), predicate=ismethod)}

    exceptions = {name: exception_description(exception) for (name, exception) in
                  getmembers(do.structures.Exceptions, predicate=isclass)}

    wiki_dir = Path("pages")

    for file in wiki_dir.iterdir():
        if not file.is_file():
            continue

        text = file.read_text().splitlines()

        found = False
        for line, content in enumerate(text):
            if content.startswith("STUB"):
                stub, replace = content.split("|")
                if replace in api_signatures:
                    text[line] = api_signatures[replace]
                elif replace in exceptions:
                    text[line] = exceptions[replace]
                found = True

        if found:
            file.write_text("\n".join(text))


if __name__ == "__main__":
    populate_wiki_stubs()
