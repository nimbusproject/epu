# Copyright 2013 University of Chicago

import unittest
import datetime
import logging
import os
import shutil
import tempfile
import time

import epu.cei_events as cei_events


# Set this to False to look at generated log files afterwards.  There will be
# many directories like /tmp/ceitestlog*
DESTROY_LOGDIR = True


class CEIEventsTestCase(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger(__name__)
        if not self._is_setup():
            self._configure()
            self.log.debug("test suite set up")

    def tearDown(self):
        if not DESTROY_LOGDIR:
            self.log.debug("logdir destruction disabled")
            return
        if not self._is_setup():
            raise Exception("tear down called without setup")
        if self.logfilehandler:
            self.log.removeHandler(self.logfilehandler)
            self.logfilehandler.close()
        shutil.rmtree(self.logdirpath)

    def _configure(self):
        tmpdir = tempfile.mkdtemp(prefix="ceitestlog")
        logfilepath = os.path.join(tmpdir, str(int(time.time())))
        f = None
        try:
            f = file(logfilepath, 'w')
            f.write("\n## auto-generated @ %s\n\n" % time.ctime())
        finally:
            if f:
                f.close()
        logfilehandler = logging.FileHandler(logfilepath)
        logfilehandler.setLevel(logging.DEBUG)
        formatstring = "%(asctime)s %(levelname)s @%(lineno)d: %(message)s"
        logfilehandler.setFormatter(logging.Formatter(formatstring))
        self.log.addHandler(logfilehandler)
        self.logfilehandler = logfilehandler
        self.logfilepath = logfilepath
        self.logdirpath = tmpdir

    def _is_setup(self):
        try:
            if self.logfilepath and self.logdirpath:
                return True
        except:
            pass
        return False

    def test_event_write(self):
        self.log.debug("something")
        cei_events.event("unittest", "TRIAL1", self.log)
        self.log.debug("something-else")
        events = cei_events.events_from_file(self.logfilepath)
        assert len(events) == 1
        assert events[0].source == "unittest"
        assert events[0].name == "TRIAL1"

    def test_manual_event_write(self):
        cruft = "some cruft %s" % cei_events.event_logtxt("unittest", "TRIAL1")
        self.log.warning(cruft)
        events = cei_events.events_from_file(self.logfilepath)

        assert len(events) == 1
        cei_events.event("unittest", "TRIAL2", self.log)
        events = cei_events.events_from_file(self.logfilepath)
        assert len(events) == 2

        cruft = "cruft2 %s" % cei_events.event_logtxt("unittest", "TRIAL3")
        self.log.warning(cruft)

        events = cei_events.events_from_file(self.logfilepath)
        assert len(events) == 3

        found = {"TRIAL1": False, "TRIAL2": False, "TRIAL3": False}
        for ev in events:
            if ev.name in found:
                found[ev.name] = True
        for val in found.values():
            assert val

    def test_timestamp(self):
        utc_now = datetime.datetime.utcnow()
        cei_events.event("unittest", "TRIAL1", self.log)
        events = cei_events.events_from_file(self.logfilepath)
        assert len(events) == 1
        ts = events[0].timestamp
        # It is possible that any of these values could have rolled over
        # between acquiring utc_now and recording the event.  But this is
        # unlikely enough that we'll keep this important UTC sanity check:
        assert ts.year == utc_now.year
        assert ts.month == utc_now.month
        assert ts.day == utc_now.day
        assert ts.hour == utc_now.hour

    def test_unique_keys(self):
        cei_events.event("unittest", "NAME", self.log)
        cei_events.event("unittest", "NAME", self.log)
        cei_events.event("unittest", "NAME", self.log)
        cei_events.event("unittest", "NAME", self.log)
        cei_events.event("unittest", "NAME", self.log)
        cei_events.event("unittest", "NAME", self.log)
        cei_events.event("unittest", "NAME", self.log)
        events = cei_events.events_from_file(self.logfilepath)
        assert len(events) == 7
        uniqs = {}
        for ev in events:
            uniqs[ev.timestamp] = None
        assert len(uniqs) == 7

    def test_extra(self):
        adict = {"hello1": "hello2"}
        cei_events.event("unittest", "TRIAL1", self.log, extra=adict)
        events = cei_events.events_from_file(self.logfilepath)
        assert len(events) == 1
        assert events[0].extra["hello1"] == "hello2"

    def test_bad_extra(self):
        self.assertRaises(Exception, cei_events.event, "unittest", "TRIAL1", self.log, extra="astring")

    def test_extra_integer_values(self):
        adict = {"hello1": 34}
        cei_events.event("unittest", "TRIAL1", self.log, extra=adict)
        events = cei_events.events_from_file(self.logfilepath)
        assert len(events) == 1
        assert events[0].extra["hello1"] == 34

    def test_extra_hierarchy(self):
        # note the conflicting "hello3" key in higher level:
        innerdict = {"hello3": "hello4"}
        adict = {"hello1": "hello2", "hello5": innerdict, "hello3": "hello6"}
        cei_events.event("unittest", "TRIAL1", self.log, extra=adict)
        events = cei_events.events_from_file(self.logfilepath)
        event = events[0]
        assert event.extra["hello1"] == "hello2"
        assert event.extra["hello3"] == "hello6"
        innerdict = event.extra["hello5"]
        assert isinstance(innerdict, dict)
        assert innerdict["hello3"] == "hello4"

    def test_newline_rules(self):
        self.assertRaises(Exception, cei_events.event, "unit\ntest", "TRIAL", self.log)
        self.assertRaises(Exception, cei_events.event, "unittest", "TRIAL\nA", self.log)
        self.assertRaises(Exception, cei_events.event, "unittest", "TRIAL", self.log, extra="some\nthing")
        self.assertRaises(Exception, cei_events.event, "unittest\n", "TRIAL", self.log)
        self.assertRaises(Exception, cei_events.event, "\nunittest", "TRIAL", self.log)
        self.assertRaises(Exception, cei_events.event, "\n", "TRIAL", self.log)

    def test_missing_rules(self):
        self.assertRaises(Exception, cei_events.event, None, "TRIAL", self.log)
        self.assertRaises(Exception, cei_events.event, "unittest", None, self.log)

    def test_event_namefilter(self):
        cei_events.event("unittest", "NM1", self.log)
        cei_events.event("unittest", "NM2", self.log)
        cei_events.event("unittest", "NM3", self.log)
        self.log.debug("something not an event")
        cei_events.event("unittest", "NM4", self.log)
        cei_events.event("unittest", "NM5", self.log)
        self.log.debug("something not an event")
        cei_events.event("unittest", "NM6", self.log)
        path = self.logfilepath
        events = cei_events.events_from_file(path, namefilter="NM")
        assert len(events) == 6

    def test_event_namefilter2(self):
        cei_events.event("unittest", "NM1", self.log)
        self.log.debug("something not an event")
        cei_events.event("unittest", "XX2", self.log)
        cei_events.event("unittest", "NM3", self.log)
        self.log.debug("something not an event")
        cei_events.event("unittest", "XX4", self.log)
        cei_events.event("unittest", "NM5", self.log)
        cei_events.event("unittest", "XX6", self.log)
        path = self.logfilepath
        events = cei_events.events_from_file(path, namefilter="NM")
        assert len(events) == 3

    def test_event_sourcefilter(self):
        cei_events.event("SRC1", "NM1", self.log)
        self.log.debug("something not an event")
        cei_events.event("SRC2", "NM2", self.log)
        cei_events.event("SRC3", "NM3", self.log)
        self.log.debug("something not an event")
        cei_events.event("SRC4", "NM4", self.log)
        cei_events.event("SRC5", "NM5", self.log)
        cei_events.event("SRC6", "NM6", self.log)
        path = self.logfilepath
        events = cei_events.events_from_file(path, sourcefilter="SRC")
        assert len(events) == 6

    def test_event_sourcefilter2(self):
        cei_events.event("SRC1", "NM1", self.log)
        self.log.debug("something not an event")
        cei_events.event("SRX2", "NM2", self.log)
        cei_events.event("SRC3", "NM3", self.log)
        self.log.debug("something not an event")
        cei_events.event("SRX4", "NM4", self.log)
        cei_events.event("SRC5", "NM5", self.log)
        cei_events.event("SRC6", "NM6", self.log)
        path = self.logfilepath
        events = cei_events.events_from_file(path, sourcefilter="SRC")
        assert len(events) == 4

    def test_event_nameandsourcefilter(self):
        cei_events.event("SRC1", "NX1", self.log)
        self.log.debug("something not an event")
        cei_events.event("SRX2", "NM2", self.log)
        cei_events.event("SRC3", "XX3", self.log)
        cei_events.event("SRX4", "XX4", self.log)
        cei_events.event("SRC5", "NM5", self.log)
        self.log.debug("something not an event")
        cei_events.event("SRC6", "NM6", self.log)
        path = self.logfilepath
        events = cei_events.events_from_file(path, sourcefilter="SRC", namefilter="NM")
        assert len(events) == 2
