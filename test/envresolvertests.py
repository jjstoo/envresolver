import datetime
import os
from typing import List
from unittest import TestCase, mock
from envresolver import EnvResolver, Types


class ParserTests(TestCase):

    def setUp(self) -> None:
        self.p = EnvResolver()

    @mock.patch.dict(os.environ, {"mystr": "myval"})
    def test_str_parsing(self):
        self.p.add_variable("mystr", str)
        self.p.resolve()
        self.assertEqual("myval", self.p.ns.mystr)
        self.assertEqual("myval", self.p.getr("mystr"))

    @mock.patch.dict(os.environ, {"nan": ""})
    def test_str_default_value(self):
        self.p.add_variable("nan", str, default="mydefaultval")
        self.p.resolve()
        self.assertEqual("mydefaultval", self.p.ns.nan)

    @mock.patch.dict(os.environ, {"mybool1": "true",
                                  "mybool2": "1",
                                  "mybool3": "yes",
                                  "mybool4": "false",
                                  "mybool5": "0",
                                  "mybool6": "no"})
    def test_bool_parsing(self):
        self.p.add_variable("mybool1", bool)
        self.p.add_variable("mybool2", bool)
        self.p.add_variable("mybool3", bool)
        self.p.add_variable("mybool4", bool)
        self.p.add_variable("mybool5", bool)
        self.p.add_variable("mybool6", bool)
        self.p.resolve()

        # Trues
        self.assertEqual(True, self.p.getr("mybool1"))
        self.assertEqual(True, self.p.getr("mybool2"))
        self.assertEqual(True, self.p.getr("mybool3"))

        # Falses
        self.assertEqual(False, self.p.getr("mybool4"))
        self.assertEqual(False, self.p.getr("mybool5"))
        self.assertEqual(False, self.p.getr("mybool6"))

    @mock.patch.dict(os.environ, {"myfloat1": "0.1",
                                  "myfloat2": "-0.65743",
                                  "myfloat3": "1",
                                  "myinvalidfloat": "float"})
    def test_float_parsing(self):
        self.p.add_variable("myfloat1", float)
        self.p.add_variable("myfloat2", float)
        self.p.add_variable("myfloat3", float)
        self.p.add_variable("myinvalidfloat", float, default=0.1)
        self.p.resolve()

        self.assertEqual(0.1, self.p.getr("myfloat1"))
        self.assertEqual(-0.65743, self.p.getr("myfloat2"))
        self.assertEqual(1.0, self.p.getr("myfloat3"))
        self.assertEqual(0.1, self.p.getr("myinvalidfloat"))

    @mock.patch.dict(os.environ, {"mydate": "2021-01-01 12:34:56",
                                  "myinvaliddate": "123"})
    def test_datetime_parsing(self):
        d = datetime.datetime.strptime("2021-01-01 12:34:56", self.p._datetime_fmt)
        self.p.add_variable("mydate", datetime.datetime)
        self.p.add_variable("myinvaliddate", datetime.datetime)
        self.p.resolve()

        self.assertEqual(d, self.p.getr("mydate"))

        # Invalid datetime
        self.assertEqual(None, self.p.getr("myinvaliddate"))

    @mock.patch.dict(os.environ, {"lst": "a,b,c,abc"})
    def test_str_list_parsing(self):
        l = ["a", "b", "c", "abc"]
        self.p.add_variable("lst", list)
        self.p.resolve()

        self.assertEqual(l, self.p.ns.lst)

    @mock.patch.dict(os.environ, {"lst": "0.1,0.2"})
    def test_float_list_parsing(self):
        l = [0.1, 0.2]
        self.p.add_variable("lst", List[float])
        self.p.resolve()

        self.assertEqual(l, self.p.ns.lst)

    @mock.patch.dict(os.environ, {"lst": "0.1,kk"})
    def test_float_list_parsing_incompatible_format(self):
        l = [0.1, 0.2]
        self.p.add_variable("lst", List[float], default=l)
        self.p.resolve()

        self.assertEqual(l, self.p.ns.lst)

    @mock.patch.dict(os.environ, {"var": "val"})
    def test_get_str_direct(self):
        self.assertEqual("val", self.p.get("var"))

    @mock.patch.dict(os.environ, {"var": "0.123"})
    def test_get_float_direct(self):
        self.assertEqual(0.123, self.p.get("var", t=float))

    @mock.patch.dict(os.environ, {"var": "rubbish"})
    def test_get_direct_default(self):
        self.assertEqual(0.123, self.p.get("var", t=float, default=0.123))