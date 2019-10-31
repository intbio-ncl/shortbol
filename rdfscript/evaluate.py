import rdflib
import logging
import pdb

from .core import (Uri,
                   Value,
                   Name,
                   LocalName,
                   Self)

from .pragma import (PrefixPragma,
                     DefaultPrefixPragma,
                     ImportPragma,
                     ExtensionPragma)

from .templating import Assignment
from .template import (Template,
                       Property,
                       Argument,
                       Expansion)

from .error import (UnknownConstruct,
                    PrefixError,
                    FailToImport,
                    NoSuchExtension,
                    ExtensionFailure)

from extensions.triples import TriplePack

def evaluate(node, env):

    return _handler_index.get(type(node), unknown_node)(node, env)

def evaluate_uri(uri, env):

    return uri

def evaluate_name(name, env):

    return env.lookup(name.uri(env)) or name.uri(env)

def evaluate_assignment(assignment, env):

    uri = assignment.name.uri(env)
    value = evaluate(assignment.value, env)

    env.assign(uri, value)

    return value

def evaluate_prefixpragma(pragma, env):

    return env.bind_prefix(pragma.prefix, evaluate(pragma.uri, env))

def evaluate_defaultprefixpragma(pragma, env):

    if not env.set_default_prefix(pragma.prefix):
        raise PrefixError(pragma.prefix, pragma.location)
    else:
        return pragma.prefix

def evaluate_importpragma(pragma, env):
    if not env.eval_import(evaluate(pragma.target, env)):
        raise FailToImport(pragma.target, env.get_current_path(), pragma.location)

    return pragma.target

def evaluate_extensionpragma(pragma, env):
    ext = env.get_extension(pragma.name)

    if not ext:
        raise NoSuchExtension(pragma.name, pragma.location)
    else:
        args = [evaluate(arg, env) for arg in pragma.args]
        return ext(*args)

def evaluate_self(myself, env):

    return env.lookup(myself.uri(env)) or myself.uri(env)

def evaluate_value(value, env):

    return value

def evaluate_template(template, env):

    template.parameterise()
    template.de_name(env)
    env.assign_template(template.name, template)

    return template.name

def evaluate_expansion(expansion, env):

    expansion.de_name(env)
    raw_triples = expansion.replace_self(expansion.as_triples(env), env)

    evaluated_triples = [(evaluate(s, env), evaluate(p, env), evaluate(o, env))
                          for (s, p, o) in raw_triples]

    final_triples = evaluated_triples
    pack = TriplePack(final_triples, env._symbol_table, env._template_table)
    for extension in expansion.get_extensions(env):
        e = evaluate(extension, env)
        e.run(pack)

    env.add_triples(pack.triples)

    return expansion.name

def evaluate_argument(argument, env):

    return evaluate(argument.value, env)

def evaluate_triple(triple, env):
    (s, p, o) = triple
    env.add_triples([(evaluate(s, env), evaluate(p, env), evaluate(o, env))])

def property_as_triple(subject, prop, env):
    return (subject, evaluate(prop.name, env), evaluate(prop.value, env))

def replace_in_triple(triple, victim, replacement):
    (s, p, o) = triple
    if s == victim: s = replacement
    if p == victim: p = replacement
    if o == victim: o = replacement

    return (s, p, o)

def unknown_node(node, env):
    raise UnknownConstruct(node, node.location)

_handler_index = {
    Uri                 : evaluate_uri,
    Name                : evaluate_name,
    PrefixPragma        : evaluate_prefixpragma,
    DefaultPrefixPragma : evaluate_defaultprefixpragma,
    ImportPragma        : evaluate_importpragma,
    ExtensionPragma     : evaluate_extensionpragma,
    Assignment          : evaluate_assignment,
    Value               : evaluate_value,
    Template            : evaluate_template,
    Expansion           : evaluate_expansion,
    Argument            : evaluate_argument,
    Self                : evaluate_self,
    type(None)          : unknown_node,
}
