# Envresolver
Envresolver is a Python library for parsing [environment variables](https://en.wikipedia.org/wiki/Environment_variable) 
to common Python datatypes. Environment variables are only accessible as pure text (string) typed variables and thus need
some manipulation to transform into any other types. `EnvResolver` class provides a nifty way of parsing the current 
environment according to given specifications.

#### Supported types (at the moment)
- str
- bool
- int
- float
- lists holding the supported types
- Json
- XML


## Usage

All variables to-be-resolved must be specified with a supported type when using `EnvResolver`. `EnvResolver` then inspects
all the specified variables and tries to parse an environment variable with the same name to the given type format. For example,
to parse simple string values:

```python
from envresolver import EnvResolver

r = EnvResolver()
r.add_parameter("var")
r.resolve()
```

If an environment variable `var1` was present in the current environment, it can be accessed by:

```python
r.var
# Or
r.get("var")
```

User can also supply default values:

```python
r.add_parameter("var2", default="default_value")
```

### Environment Variables with Type Conversions

As stated before, `EnvResolver` also supports automated type conversions for environment variables. Variable types can
be specified as shown:

```python
r.add_parameter("var", t=int, default=-1)
```

Let's imagine the current environment would hold the variable `var` with a value of `"5"`. By running `EnvResolver.resolve`, 
it would be automatically parsed. However, if the environment variable `var` would hold an incompatible value, `"_"`, as an example,
the parsing would fail and `r.var` would hold the default value, if one was given:

```python
from envresolver import EnvResolver

# export var=5
r = EnvResolver()
r.add_parameter("var", t=int, default=-1)
r.resolve()
r.var # 5

# export var=_
r = EnvResolver()
r.add_parameter("var", t=int, default=-1)
r.resolve()
r.var # -1
```

### Advanced Types

`LSFOpt` currently support also some more advanced types of variables, such as lists, Json and XML. Lists have full support
of type hinting and will try to convert all elements accordingly:

```python
from typing import List
from envresolver import EnvResolver

# export my_list=1,2,3,4
r = EnvResolver()
r.add_parameter("my_list", t=List[int])
r.resolve()
r.my_list # [1, 2, 3, 4]
```

Json and XML are supported via custom type notations stored in `envresolver.Types`. Json and XML will be parsed using Pythons built-in
`json` and `xml` modules. Json parsing will output native python lists/dicts and XML results will be of type `xml.etree.ElementTree.Element`.
Here is an example on Json parsing:

```python
from envresolver import EnvResolver, Types

# export json={"key": "val"}
r = EnvResolver()
r.add_parameter("json", t=Types.Json)
r.resolve()
r.json # {"key": "val"}
```

### Custom Types

Users can supply `LSFOpt` with custom parsers as well as override existing ones. Below is an example of using a custom parser
for reading data into a user-defined class:

```python
from envresolver import EnvResolver

class MyData:
    def __init__(self, a, b):
        self.a = a
        self.b = b

def my_data_converter(e: str):
    s = e.split(".")
    
    # Raise ValueError if the given environment variable
    #  is in wrong format
    if len(s) != 2:
        raise ValueError
    
    # Return parsed data
    return MyData(a=s[0], b=s[1])
        
# export data=john.smith
r = EnvResolver()
r.add_converter(MyData, my_data_converter)
r.add_parameter("data", t=MyData)
r.resolve()
r.data # MyData(a = "john", b = "smith")
```
