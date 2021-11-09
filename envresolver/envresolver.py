from os import getenv
from sys import stderr
from json import loads
import xml.etree.ElementTree as ET
from typing import Type, Any, Callable, get_origin, get_args


class Types:
    class Json:
        """Json type representation"""
    class Xml:
        """XML type representation"""


class EnvResolver:
    """
    Class for resolving environment variables with attention to type.

    Since environment variables are generally accessible only with an apparent
    string-type, type conversions and deductions have to conducted explicitly.
    """

    class _Var:
        """
        Representation of a single variable
        """
        def __init__(self, name, t, val):
            self.name: str = name
            self.t: Type = t
            self.val = val

    def __init__(self, list_separator: str = ",", silent: bool = False):
        """
        Initializes the instance and sets verbosity

        :param list_separator: List separator symbol
        :param silent: If True, error messages will be printed to `stderr`
        """
        self._silent = silent
        self._list_separator = list_separator
        self._params: {str, EnvResolver._Var} = {}
        self._converters: {Type: Callable} = {
            str: None,
            int: lambda e: int(e),
            float: lambda e: float(e),
            bool: EnvResolver._get_bool,
            Types.Json: EnvResolver._get_json,
            Types.Xml: EnvResolver._get_xml,
            list: EnvResolver._get_list
        }

    @staticmethod
    def _get_bool(e: str):
        t = ("true", "y", "yes", "1")
        f = ("false", "n", "no", "0")
        lower = e.lower()
        if lower in t:
            return True
        elif lower in f:
            return False
        else:
            raise ValueError

    @staticmethod
    def _get_list(e: str, sep: str):
        return e.split(sep)

    @staticmethod
    def _get_json(e: str):
        return loads(e)

    @staticmethod
    def _get_xml(e: str):
        return ET.fromstring(e)

    def _get_from_env(self, p: _Var):
        env = getenv(p.name)
        if not env:
            return
        try:
            if p.t == str:
                p.val = env
            elif p.t == list or get_origin(p.t) == list:
                l = self._converters[list](env, self._list_separator)
                if p.t == list:
                    p.val = l
                    return
                else:
                    t_content = get_args(p.t)[0]
                    values_temp = []
                    for item in l:
                        values_temp.append(self._converters[t_content](item))
                    p.val = values_temp
            else:
                p.val = self._converters[p.t](env)

        except ValueError:
            if not self._silent:
                print(f"Variable {p.name} with type {p.t} found in the "
                      f"current env with invalid value: {env}", file=stderr)
            return

    def add_converter(self, t: Type, c: Callable):
        """
        Adds a custom converter/parser to the instance

        :param t: Converter type
        :param c: Converter callable accepting a single string-type argument
        :return: None
        """
        if not t:
            raise TypeError("Type cannot be None")
        if not callable(c):
            raise TypeError(f"parameter c must be a callable, got "
                            f"{str(type(c))}")
        self._converters[t] = c

    def add_parameter(self, name: str, t: Type = str, default: Any = None):
        """
        Adds a parameter for resolving

        :param name: Parameter name
        :param t: Parameter type
        :param default: Default value
        :return: None
        """
        if t not in self._converters and get_origin(t) not in self._converters:
            raise NotImplementedError(f"Conversion support for type {str(t)} "
                                      f"not added!")
        self._params[name] = EnvResolver._Var(name, t, default)

    def resolve(self):
        """
        Resolves all configured parameters

        :return: None
        """
        for p in self._params.values():
            self._get_from_env(p)
            setattr(self, p.name, p.val)

    def get(self, name):
        """
        Get a parameter value

        :param name: Parameter name
        :return: Parameter value
        """
        return self._params[name].val

