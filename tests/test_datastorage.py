# -*- coding: utf-8 -*-
import random
import shutil
import tempfile

import os

from .context import ztom

import unittest


class DataStorageTestSuite(unittest.TestCase):

    def setUp(self):
        self.folder = os.path.join(tempfile.gettempdir(), 'storage' + str(random.randint(1, 100000)))
        self.storage = ztom.DataStorage(self.folder)

    def tearDown(self):
        if not os.path.isdir(self.folder):
            raise ValueError('Folder don\'t exist: %s' % self.folder)
        self.storage.stop()
        shutil.rmtree(self.folder)

    def test_save(self):
        self.storage.register('pepe', ['a', 'b', 'c'])
        self.storage.save('pepe', [1, '2', 2.0])
        self.assertEqual('a,b,c\n1,2,2.0\n', self.file_contents('pepe'))

        self.storage.register('bobo', ['x', 'y'])
        self.storage.save('bobo', ['kkk', 'mmm'])
        self.assertEqual('x,y\nkkk,mmm\n', self.file_contents('bobo'))

        self.storage.save('pepe', [2, '3', 4.0])
        self.assertEqual('a,b,c\n1,2,2.0\n2,3,4.0\n', self.file_contents('pepe'))

    def test_save_dict(self):
        self.storage.register('pepe', ['a', 'b', 'c'])
        self.storage.save_dict('pepe', {'b': '2', 'a': 1, 'c': 2.0})
        self.assertEqual('a,b,c\n1,2,2.0\n', self.file_contents('pepe'))

    def test_save_dict_all(self):
        self.storage.register('pepe', ['a'])
        self.storage.save_dict_all('pepe', [{'a': '1'}, {'a': '2'}])
        self.assertEqual('a\n1\n2\n', self.file_contents('pepe'))

    def test_save_all(self):
        self.storage.register('pepe', ['a', 'b', 'c'])
        self.storage.save_all('pepe', [['1', '2', '3'], ['4', '5', '6']])
        self.assertEqual('a,b,c\n1,2,3\n4,5,6\n', self.file_contents('pepe'))

    def test_missing_values(self):
        self.storage.register('pepe', ['a', 'b'])
        self.storage.save_dict_all('pepe', [{'a': '1'}, {'b': '2'}])
        self.assertEqual('a,b\n1,\n,2\n', self.file_contents('pepe'))

    def file_contents(self, type_name):
        with open(self.storage.path(type_name), 'r') as file:
            return file.read()

    def test_get_nested_from_dict(self):
        column = "column_name__section__subsection__field_name"
        dict = {
            "column_name": {
                "section": {
                    "subsection":
                        {"field_name": "value"}
                }
            }
        }
        val = self.storage._get_nested_from_dict(dict, column)
        self.assertEqual("value", val)

        column = "field_name"
        dict = {"field_name": "value2"}

        val = self.storage._get_nested_from_dict(dict, column)
        self.assertEqual("value2", val)

        self.storage.register('pepe', ['a__a1__a-2', 'b__b1_b2', 'c'])
        self.storage.save_dict('pepe',
                               {'b':
                                    {"b1_b2": "val_b"}
                                     ,
                                'a': {
                                    "a1":
                                        {"a-2": "val_a2"}
                                },
                                'c': 2.0})

        self.assertEqual('a__a1__a-2,b__b1_b2,c\nval_a2,val_b,2.0\n', self.file_contents('pepe'))


