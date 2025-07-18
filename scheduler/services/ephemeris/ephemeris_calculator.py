# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

from typing import final

from astropy.coordinates import SkyCoord
from astropy.time import Time, TimeDelta
import astropy.units as u
import numpy as np

from lucupy.minimodel import NonsiderealTarget, Site
from lucupy.meta import Singleton
from lucupy.timeutils import time2slots

from scheduler.config import config
from scheduler.services.horizons import horizons_session
from scheduler.services.logger_factory import create_logger

__all__ = [
    'EphemerisCalculator'
]

logger = create_logger(__name__)


@final
class EphemerisCalculator(metaclass=Singleton):
    """
    Uses either the cached files or the HorizonsClient - in that order - to fetch the ephemeris data
    for a given target from a specified start time and a given number of time slots.
    """
    # Use a 1 min timeslot for Horizons queries, this is sampled later to the time grid used by the scheduler instance
    _DEFAULT_TIMESLOT_LENGTH: TimeDelta = TimeDelta(60.0 * u.second)
    # _DEFAULT_TIMESLOT_LENGTH: TimeDelta = TimeDelta(config.collector.time_slot_length * u.min)

    def calculate_coordinates(self,
                              site: Site,
                              target: NonsiderealTarget,
                              start_lookup_time: Time,
                              end_lookup_time: Time) -> SkyCoord:
        """
        Perform a lookup for the ephemeris data for a given nonsidereal target at a given site with a specific airmass.
        The lookup is done from the start_lookup_time to the end_lookup_time inclusive at one minute intervals.
        This flexibility here is to allow lookups larger than between twilights, e.g. from sunset to sunrise.
        """
        # TODO: Determine if the lookup times are tz-aware and UTC or local.
        # TODO: We need them to be UTC for the Horizons client to work.
        # TODO: Then we want to make them local for actual computation?
        if start_lookup_time.isscalar:
            start_lookup_time_py = start_lookup_time.to_datetime()
        elif start_lookup_time.value.size == 1:
            start_lookup_time_py = start_lookup_time[0].to_datetime()
        else:
            logger.error('start_lookup_time must be a scalar or s ingle value')
            raise ValueError('start_lookup_time must be a scalar or single value.')

        if end_lookup_time.isscalar:
            end_lookup_time_py = end_lookup_time.to_datetime()
        elif end_lookup_time.value.size == 1:
            end_lookup_time_py = end_lookup_time[0].to_datetime()
        else:
            logger.error('end_lookup_time must be a scalar or single value.')
            raise ValueError('end_lookup_time must be a scalar or single value.')

        if start_lookup_time_py > end_lookup_time_py:
            logger.error(f'Cannot calculate ephemeris for end date that occurs before start date.')
            raise ValueError(f'Cannot calculate ephemeris for end date that occurs before start date.')

        with horizons_session(site, start_lookup_time.to_datetime(), end_lookup_time.to_datetime(),
                              time_slot_length=1) as hs:
                                # time_slot_length = config.collector.time_slot_length) as hs:

            # We don't care about the time. It should match up with the above times.
            coords = hs.get_ephemerides(target).coordinates

            # Expected number of slots. Add 1 to make inclusive.
            expected_slots = time2slots(EphemerisCalculator._DEFAULT_TIMESLOT_LENGTH.to_datetime(),
                                        end_lookup_time_py - start_lookup_time_py) + 1

            if abs(expected_slots - len(coords)) > 10:
                logger.warning(f'Ephemeris expected {expected_slots} entries, but received {len(coords)} entries.')

            # Extract into arrays of ra and dec. NOTE that these are calculated in radians and not degrees.
            ras = np.array([c.ra for c in coords])
            decs = np.array([c.dec for c in coords])
            return SkyCoord(ra=ras * u.rad, dec=decs * u.rad, frame='icrs')