#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import xml.etree.ElementTree as ET
from pyowm.exceptions import parse_response_error
from pyowm.utils import formatting, timestamps, xml
from pyowm.uvindexapi30.xsd.xmlnsconfig import (
    UVINDEX_XMLNS_URL, UVINDEX_XMLNS_PREFIX)
from pyowm.weatherapi25 import location


def uv_intensity_to_exposure_risk(uv_intensity):
    # According to figures in: https://en.wikipedia.org/wiki/Ultraviolet_index
    if 0.0 <= uv_intensity < 2.9:
        return 'low'
    elif 2.9 <= uv_intensity < 5.9:
        return 'moderate'
    elif 5.9 <= uv_intensity <  7.9:
        return 'high'
    elif 7.9 <= uv_intensity < 10.9:
        return 'very high'
    else:
        return 'extreme'


class UVIndex:
    """
    A class representing the UltraViolet Index observed in a certain location
    in the world. The location is represented by the encapsulated *Location* object.

    :param reference_time: GMT UNIXtime telling when the UV data have been measured
    :type reference_time: int
    :param location: the *Location* relative to this UV observation
    :type location: *Location*
    :param value: the observed UV intensity value
    :type value: float
    :param reception_time: GMT UNIXtime telling when the observation has
        been received from the OWM Weather API
    :type reception_time: int
    :returns: an *UVIndex* instance
    :raises: *ValueError* when negative values are provided as reception time or
      UV intensity value

    """

    def __init__(self, reference_time, location, value, reception_time):
        if reference_time < 0:
            raise ValueError("'referencetime' must be greater than 0")
        self._reference_time = reference_time
        self._location = location
        if value < 0.0:
            raise ValueError("'UV intensity must be greater than 0")
        self._value = value
        if reception_time < 0:
            raise ValueError("'reception_time' must be greater than 0")
        self._reception_time = reception_time

    def get_reference_time(self, timeformat='unix'):
        """
        Returns the GMT time telling when the UV has been observed
          from the OWM Weather API

        :param timeformat: the format for the time value. May be:
            '*unix*' (default) for UNIX time
            '*iso*' for ISO8601-formatted string in the format ``YYYY-MM-DD HH:MM:SS+00``
            '*date* for ``datetime.datetime`` object instance
        :type timeformat: str
        :returns: an int or a str
        :raises: ValueError when negative values are provided

        """
        return formatting.timeformat(self._reference_time, timeformat)

    def get_reception_time(self, timeformat='unix'):
        """
        Returns the GMT time telling when the UV has been received from the API

        :param timeformat: the format for the time value. May be:
            '*unix*' (default) for UNIX time
            '*iso*' for ISO8601-formatted string in the format ``YYYY-MM-DD HH:MM:SS+00``
            '*date* for ``datetime.datetime`` object instance
        :type timeformat: str
        :returns: an int or a str
        :raises: ValueError when negative values are provided

        """
        return formatting.timeformat(self._reception_time, timeformat)

    def get_location(self):
        """
        Returns the *Location* object for this UV observation

        :returns: the *Location* object

        """
        return self._location

    def get_value(self):
        """
        Returns the UV intensity for this observation

        :returns: float

        """
        return self._value

    def get_exposure_risk(self):
        """
        Returns a string stating the risk of harm from unprotected sun exposure
        for the average adult on this UV observation
        :return: str
        """
        return uv_intensity_to_exposure_risk(self._value)

    @classmethod
    def from_dict(cls, the_dict):
        """
        Parses an *UVIndex* instance out of raw JSON data. Only certain properties of the data are used: if these
        properties are not found or cannot be parsed, an error is issued.

        :param the_dict: the input dict
        :type the_dict: dict
        :returns: an *UVIndex* instance or ``None`` if no data is available
        :raises: *ParseResponseError* if it is impossible to find or parse the
            data needed to build the result, *APIResponseError* if the input dict embeds an HTTP status error

        """
        if the_dict is None:
            raise parse_response_error.ParseResponseError('Data is None')
        try:
            # -- reference time
            reference_time = the_dict['date']

            # -- reception time (now)
            reception_time = timestamps.now('unix')

            # -- location
            lon = float(the_dict['lon'])
            lat = float(the_dict['lat'])
            place = location.Location(None, lon, lat, None)

            # -- UV intensity
            uv_intensity = float(the_dict['value'])
        except KeyError:
            raise parse_response_error.ParseResponseError(''.join([__name__, ': impossible to parse UV Index']))
        return UVIndex(reference_time, place, uv_intensity, reception_time)

    def to_dict(self):
        """Dumps object to a dictionary

        :returns: a `dict`

        """
        return {"reference_time": self._reference_time,
                "location": self._location.to_dict(),
                "value": self._value,
                "reception_time": self._reception_time}

    def __repr__(self):
        return "<%s.%s - reference time=%s, reception time=%s, location=%s, " \
               "value=%s>" % (
                    __name__,
                    self.__class__.__name__,
                    self.get_reference_time('iso'),
                    self.get_reception_time('iso'),
                    str(self._location),
                    str(self._value))
