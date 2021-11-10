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
        self.p.add_parameter("mystr", str)
        self.p.resolve()
        self.assertEqual("myval", self.p.mystr)
        self.assertEqual("myval", self.p.get("mystr"))

    @mock.patch.dict(os.environ, {"nan": ""})
    def test_str_default_value(self):
        self.p.add_parameter("nan", str, default="mydefaultval")
        self.p.resolve()
        self.assertEqual("mydefaultval", self.p.nan)

    @mock.patch.dict(os.environ, {"mybool1": "true",
                                  "mybool2": "1",
                                  "mybool3": "yes",
                                  "mybool4": "false",
                                  "mybool5": "0",
                                  "mybool6": "no"})
    def test_bool_parsing(self):
        self.p.add_parameter("mybool1", bool)
        self.p.add_parameter("mybool2", bool)
        self.p.add_parameter("mybool3", bool)
        self.p.add_parameter("mybool4", bool)
        self.p.add_parameter("mybool5", bool)
        self.p.add_parameter("mybool6", bool)
        self.p.resolve()

        # Trues
        self.assertEqual(True, self.p.get("mybool1"))
        self.assertEqual(True, self.p.get("mybool2"))
        self.assertEqual(True, self.p.get("mybool3"))

        # Falses
        self.assertEqual(False, self.p.get("mybool4"))
        self.assertEqual(False, self.p.get("mybool5"))
        self.assertEqual(False, self.p.get("mybool6"))

    @mock.patch.dict(os.environ, {"myfloat1": "0.1",
                                  "myfloat2": "-0.65743",
                                  "myfloat3": "1",
                                  "myinvalidfloat": "float"})
    def test_float_parsing(self):
        self.p.add_parameter("myfloat1", float)
        self.p.add_parameter("myfloat2", float)
        self.p.add_parameter("myfloat3", float)
        self.p.add_parameter("myinvalidfloat", float, default=0.1)
        self.p.resolve()

        self.assertEqual(0.1, self.p.get("myfloat1"))
        self.assertEqual(-0.65743, self.p.get("myfloat2"))
        self.assertEqual(1.0, self.p.get("myfloat3"))
        self.assertEqual(0.1, self.p.get("myinvalidfloat"))

    @mock.patch.dict(os.environ, {"mydate": "2021-01-01 12:34:56",
                                  "myinvaliddate": "123"})
    def test_datetime_parsing(self):
        d = datetime.datetime.strptime("2021-01-01 12:34:56", self.p._datetime_fmt)
        self.p.add_parameter("mydate", datetime.datetime)
        self.p.add_parameter("myinvaliddate", datetime.datetime)
        self.p.resolve()

        self.assertEqual(d, self.p.get("mydate"))

        # Invalid datetime
        self.assertEqual(None, self.p.get("myinvaliddate"))

    @mock.patch.dict(os.environ, {"lst": "a,b,c,abc"})
    def test_str_list_parsing(self):
        l = ["a", "b", "c", "abc"]
        self.p.add_parameter("lst", list)
        self.p.resolve()

        self.assertEqual(l, self.p.lst)

    @mock.patch.dict(os.environ, {"lst": "0.1,0.2"})
    def test_float_list_parsing(self):
        l = [0.1, 0.2]
        self.p.add_parameter("lst", List[float])
        self.p.resolve()

        self.assertEqual(l, self.p.lst)

    @mock.patch.dict(os.environ, {"lst": "0.1,kk"})
    def test_float_list_parsing_incompatible_format(self):
        l = [0.1, 0.2]
        self.p.add_parameter("lst", List[float], default=l)
        self.p.resolve()

        self.assertEqual(l, self.p.lst)