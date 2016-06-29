# -*- coding: utf-8 -*-
# --------------------------------
# Copyright (c) 2016 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------

from canopsis.middleware.core import Middleware
from canopsis.schema.core import Schema
from canopsis.schema.lang.json import JsonSchema
from canopsis.schema.transformation.core import Transformation
from canopsis.mongo.core import MongoStorage

from unittest import main, TestCase, SkipTest
import jsonpatch
import jsonschema
import json
import os

class TestUseCase(TestCase):


    def setUp(self):
        """inititation of the test"""

        self.path_transfo = '/home/julie/Documents/canopsis/sources/python/schema/etc/schema/transformation_dico.json'
        self.path_v1 = '/home/julie/Documents/canopsis/sources/python/schema/etc/schema/V1_schema.json'
        self.path_v2 = '/home/julie/Documents/canopsis/sources/python/schema/etc/schema/V2_schema.json'

        self.schema_class = JsonSchema
        self.transformation_class = Transformation

        self.schema = self.schema_class(self.path_transfo)
        self.transfo = self.transformation_class(self.schema)

    def test_use(self):
        """use case of a python dictionary migration"""

        schema_transfo = self.schema.getresource(self.path_transfo)
        schema_V1 = self.schema.getresource(self.path_v1)
        schema_V2 = self.schema.getresource(self.path_v2)

        data = {'version':'1.0.0', 'info':'blabla'}

        self.schema.validate(data)

        output = schema_transfo['output']
        self.assertEqual(output, '~/dataV2.json')

        result = self.transfo.apply_patch(data)

        output = os.path.expanduser(output)
        output = os.path.abspath(output)

        self.assertEqual(output, '/opt/canopsis/dataV2.json')

        self.schema.save(result, output)


if __name__ == '__main__':
    main()