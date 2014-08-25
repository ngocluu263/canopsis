#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------
# Copyright (c) 2014 "Capensis" [http://www.capensis.com]
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
# ---------------------------------

from logging import getLogger
from unittest import main, TestCase
from canopsis.organisation.rights import Rights
import pprint

class RightsTest(TestCase):

    def setUp(self):
        self.logger = getLogger()
        self.rights = Rights()
        self.data_types = ['profiles', 'composites', 'roles']
        self.printer = pprint.PrettyPrinter(indent=4)

    def test(self):
        # Test creation of composites
        rights = {
            'rights': {
                '1234': {'checksum': 15},
                '1235': {'checksum': 8},
                '1236': {'checksum': 12},
                '1237': {'checksum': 1},
                '1238': {'checksum': 15},
                '1239': {'checksum': 15},
                '1240': {'checksum': 8},
                '1241': {'checksum': 8}}
            }
        rights_scnd = {
            'rights': {
                '2344': {'checksum': 15},
                '2345': {'checksum': 8},
                '2346': {'checksum': 12},
                '2347': {'checksum': 1},
                '2348': {'checksum': 15},
                '2349': {'checksum': 15},
                '4210': {'checksum': 8},
                '4211': {'checksum': 8}}
            }
        sample_user = {
            'contact': {
                'mail': 'jharris@scdp.com',
                'phone_number': '+33678695041',
                'adress': '1271 6th Avenue, Rockefeller Cent., NYC, New York'},
            'name': 'Joan Harris',
            'role': '',
            '_id': '1407160264.joan.harris.manager'}

        # delete everything before startin
        self.printer.pprint(self.rights['composite_storage'].get_elements())

        self.rights.delete_composite('composite_test1')
        self.rights.delete_composite('composite_test2')

        self.printer.pprint({})

        self.printer.pprint(self.rights['composite_storage'].get_elements())

        # basic creation
        self.rights.create_composite('composite_test1', rights)
        self.rights.create_composite('composite_test2', rights_scnd)

        # basic profile creation
        self.rights.create_profile('profile_test1', 'composite_test1')
        self.rights.create_profile('profile_test2', 'composite_test2')

        # "add" composite_test2 to profile_test1
        print self.rights.add_composite('profile_test1',
                                        'profiles_storage',
                                        'composite_test2')

        # create new role and assign it to the user
        sample_user['role'] = self.rights.create_role('role_test1bis',
                                                      'profile_test1')


        # create second sample role
        self.rights.create_role('role_test2',
                                'profile_test2')


        # Basic check
        self.assertEqual(
            self.rights.check_user_rights(
                sample_user['role'], '1237', 1), True)

        self.assertEqual(
            self.rights.check_user_rights(
                sample_user['role'], '1237', 12), False)

        # Add permissions to the rights
        self.rights.add('composite_test1', 'profiles_storage', '1237', 12)

        # Check shall return True now
        self.assertEqual(
            self.rights.check_user_rights(
                sample_user['role'], '1237', 12), True)


if __name__ == '__main__':
    main()
