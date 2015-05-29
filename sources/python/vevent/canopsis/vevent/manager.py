# -*- coding: utf-8 -*-
# --------------------------------
# Copyright (c) 2015 "Capensis" [http://www.capensis.com]
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

"""
"""

from canopsis.common.init import basestring
from canopsis.configuration.configurable.decorator import (
    conf_paths, add_category
)
from canopsis.middleware.registry import MiddlewareRegistry

from time import time

from icalendar import Event

from dateutil.rrule import rrulestr

from calendar import timegm

from datetime import datetime, time as datetime_time, timedelta

from uuid import uuid4 as uuid

from sys import maxsize

CONF_PATH = 'vevent/vevent.conf'
CATEGORY = 'VEVENT'


@add_category(CATEGORY)
@conf_paths(CONF_PATH)
class VEventManager(MiddlewareRegistry):
    """Manage virtual event data.

    Such vevent are technically an expression which respects the icalendar
    specification ftp://ftp.rfc-editor.org/in-notes/rfc2445.txt.

    A vevent document contains several values. Each value contains
    an icalendar expression (dtstart, rrule, duration) and an array of
    behavior entries:

    {
        id: document_id,
        source: source element id,
        dtstart: datetime start,
        dtend: datetime end,
        duration: vevent duration,
        freq: vevent freq,
        vevent: vevent ical format value,
        info: data information
    }.
    """

    STORAGE = 'vevent_storage'  #: vevent storage name

    UID = 'uid'  #: document id
    SOURCE = 'source'  #: source field name
    DTSTART = 'dtstart'  #: dtstart field name
    DTEND = 'dtend'  #: dtend field name
    DURATION = 'duration'  #: duration field name
    FREQ = 'freq'  #: freq field name
    VEVENT = 'vevent'  #: vevent value field name

    def __init__(self, vevent_storage=None, *args, **kwargs):
        """
        :param Storage vevent_storage: vevent storage.
        """

        super(VEventManager, self).__init__(*args, **kwargs)
        # set storage if given
        if vevent_storage is not None:
            self[VEventManager.STORAGE] = vevent_storage

    def _get_document_properties(self, document):
        """Get properties from a document.

        :param dict document: document from where get properties.
        :return: document properties in a dictionary.
        :rtype: dict
        """

        return {}

    def _get_vevent_properties(self, vevent):
        """Get information from a vevent.

        :param Event vevent: vevent from where get information.
        :return: vevent information in a dictionary.
        :rtype: dict
        """

        return {}

    def get_by_uids(
        self, uids,
        limit=0, skip=0, sort=None, projection=None, with_count=False
    ):
        """Get documents by uids.

        :param list uids: list of document uids.
        :param int limit: max number of elements to get.
        :param int skip: first element index among searched list.
        :param sort: contains a list of couples of field (name, ASC/DESC)
            or field name which denots an implicitelly ASC order.
        :type sort: list of {(str, {ASC, DESC}}), or str}
        :param dict projection: key names to keep from elements.
        :param bool with_count: If True (False by default), add count to the
            result.
        :return: documents where uids are in uids.
        :rtype: list
        """

        documents = self[VEventManager.STORAGE].get_element(
            ids=uids,
            limit=limit, skip=skip, sort=sort, projection=projection,
            with_count=with_count
        )

        if with_count:
            result = list(documents[0]), documents[1]
        else:
            result = list(documents[0])

        return result

    def values(
        self, sources=None, dtstart=None, dtend=None, query=None,
        limit=0, skip=0, sort=None, projection=None, with_count=False
    ):
        """Get source vevent document values.

        :param list sources: sources from where get values. If None, use all
            sources.
        :param int dtstart: vevent dtstart (default 0).
        :param int dtend: vevent dtend (default sys.maxsize).
        :param dict query: additional filtering query to apply in the search.
        :param int limit: max number of elements to get.
        :param int skip: first element index among searched list.
        :param sort: contains a list of couples of field (name, ASC/DESC)
            or field name which denots an implicitelly ASC order.
        :type sort: list of {(str, {ASC, DESC}}), or str}
        :param dict projection: key names to keep from elements.
        :param bool with_count: If True (False by default), add count to the
            result.
        :return: matchable documents.
        :rtype: list
        """

        # initialize query
        if query is None:
            query = {}

        # put sources in query if necessary
        if sources is not None:
            query[VEventManager.SOURCE] = {'$in': sources}
        # put dtstart and dtend in query
        if dtstart is None:
            dtstart = 0
        if dtend is None:
            dtend = maxsize

        query['$and'] = [
            {
                '$or': [
                    {VEventManager.DTSTART: {'$gte': dtstart}},
                    {VEventManager.DTSTART: {'$lte': dtend}}
                ]
            },
            {
                '$or': [
                    {VEventManager.DTEND: {'$gte': dtstart}},
                    {VEventManager.DTEND: {'$lte': dtend}}
                ]
            }
        ]

        documents = self[VEventManager.STORAGE].find_elements(
            query=query,
            limit=limit, skip=skip, sort=sort, projection=projection,
            with_count=with_count
        )

        if with_count:
            result = list(documents[0]), documents[1]
        else:
            result = list(documents)

        return result

    def whois(self, sources=None, dtstart=None, dtend=None, query=None):
        """Get a set of sources which match with timed condition and query.

        :param list sources: sources from where get values. If None, use all
            sources.
        :param int dtstart: vevent dtstart (default 0).
        :param int dtend: vevent dtend (default sys.maxsize).
        :param dict query: additional filtering query to apply in the search.
        :return: sources.
        :rtype: set
        """

        values = self.values(
            sources=sources, dtstart=dtstart, dtend=dtend, query=query
        )

        result = set([value[VEventManager.SOURCE] for value in values])

        return result

    def put(self, vevents, source=None, cache=False):
        """Add vevents (and optionally data) related to input source.

        :param str source: vevent source if not None.
        :param list vevents: vevents (document, str or ical vevent).
        :param dict info: vevent info.
        :param bool cache: if True (default False), use storage cache.
        :return: new documents.
        :rtype: list
        """

        result = []

        for vevent in vevents:

            document = None

            if isinstance(vevent, dict):

                document = vevent
                # get uid
                uid = document.get(VEventManager.UID)
                if not uid:
                    uid = str(uuid())
                    document[VEventManager.UID] = uid
                # get source
                source = document.get(VEventManager.SOURCE, source)
                # get dtstart
                dtstart = document[VEventManager.DTSTART]
                # get dtend
                dtend = document[VEventManager.DTEND]
                # get duration
                duration = document[VEventManager.DURATION]
                # get freq
                freq = document[VEventManager.FREQ]
                # get vevent
                vevent = document[VEventManager.VEVENT]

                # construct the right vevent if False
                if not vevent:
                    # prepare vevent kwargs with specific parameters
                    kwargs = self._get_document_properties(document=document)
                    # prepare vevent properties
                    kwargs[VEventManager.UID] = uid
                    if source:
                        kwargs[VEventManager.SOURCE] = source
                    if dtstart:
                        kwargs[VEventManager.DTSTART] = datetime.fromtimestamp(
                            dtstart
                        )
                    if dtend:
                        kwargs[VEventManager.DTEND] = datetime.fromtimestamp(
                            dtend
                        )
                    if duration:
                        kwargs[VEventManager.DURATION] = timedelta(duration)
                    if freq:
                        kwargs[VEventManager.FREQ] = freq
                    # updat vevent field in document
                    document[VEventManager.VEVENT] = Event(**kwargs).to_ical()

            # if document has to be generated ...
            else:
                # ensure vevent is an ical format
                if isinstance(vevent, basestring):
                    vevent = Event.from_ical(vevent)
                # prepare the document with specific properties
                document = self._get_vevent_properties(vevent=vevent)
                # get dtstart
                dtstart = vevent.get(VEventManager.DTSTART, 0)
                if isinstance(dtstart, datetime):
                    dtstart = timegm(dtstart.timetuple())
                # get dtend
                dtend = vevent.get(VEventManager.DTEND, 0)
                if isinstance(dtend, datetime):
                    dtend = timegm(dtend.timetuple())
                # get duration
                duration = vevent.get(VEventManager.DURATION)
                # get freq
                freq = vevent.get(VEventManager.FREQ)
                # get uid
                uid = vevent.get(VEventManager.UID)
                if not uid:
                    uid = str(uuid())
                # prepare the document
                document.update({
                    VEventManager.UID: uid,
                    VEventManager.SOURCE: source,
                    VEventManager.DTSTART: dtstart,
                    VEventManager.DTEND: dtend,
                    VEventManager.DURATION: duration,
                    VEventManager.FREQ: freq,
                    VEventManager.VEVENT: vevent.to_ical()
                })

            self[VEventManager.STORAGE].put_element(
                _id=uid, element=document
            )

            document['_id'] = uid

            result.append(document)

        return result

    def remove(self, uids=None, cache=False):
        """Remove elements from storage where uids are given.

        :param list uids: list of document uids to remove from storage
            (default all empty storage documents).
        """

        result = self[VEventManager.STORAGE].remove_elements(
            ids=uids, cache=cache
        )

        return result

    def remove_by_source(self, sources=None, cache=False):
        """Remove vevent documents related to input sources.

        :param list sources: sources from where remove related vevent
            documents.
        """
        _filter = {}

        if sources is not None:
            _filter[VEventManager.SOURCE] = {'$in': sources}

        result = self[VEventManager.STORAGE].remove_elements(
            _filter=_filter, cache=cache
        )

        return result
