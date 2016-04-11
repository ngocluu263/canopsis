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
# ---------------------------------
from __future__ import unicode_literals

from canopsis.common.init import Init
from logging import INFO, DEBUG, FileHandler, Formatter
from os.path import join
from sys import prefix as sys_prefix


class Publisher(object):

    def __init__(self, logging_level=INFO, *args, **kwargs):
        super(Publisher, self).__init__(*args, **kwargs)

        self.logging_level = logging_level

        logHandler = FileHandler(
            filename=join(
                sys_prefix, 'var', 'log', 'engines', 'network_latency.log'
            )
        )

        logHandler.setFormatter(
            Formatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s"
            )
        )

        self.logger.addHandler(logHandler)

        init = Init()
        self.logger = init.getLogger(
            'network_latency', logging_level=self.logging_level)

    def publish(self, message, *args, **kwargs):
        self.logger.info('message')
