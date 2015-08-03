#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2015, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""Send seismic data to htmengine"""

import argparse
import datetime
import json
import os
import pandas
import sys
import time

from nta.utils import message_bus_connector
from nta.utils.config import Config
from obspy import UTCDateTime
from obspy.fdsn import Client



appConfig = Config("application.conf", os.environ["APPLICATION_CONFIG_PATH"])
MESSAGE_QUEUE_NAME = appConfig.get("metric_listener", "queue_name")



def sendSample(bus, metricName, value, epochTimestamp):
  singleDataPoint = "%s %r %d" % (metricName, float(value), epochTimestamp)
  msg = json.dumps(dict(protocol="plain", data=[singleDataPoint]))
  bus.publish(mqName=MESSAGE_QUEUE_NAME, body=msg, persistent=True)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--dataFile", type=str, default=None,
    help="File of past data to use")
  args = parser.parse_args()

  bus = message_bus_connector.MessageBusConnector()
  metricName = "seismic-{}".format(args.dataFile) if args.dataFile is not None else "seismic"

  if args.dataFile is None:
    client = Client("IRIS")
    ncInventory = client.get_stations(network="NC", level="channel",
      starttime=UTCDateTime(datetime.datetime.today()))
    channels = ncInventory.get_contents()["channels"]
    coordinates = [ncInventory.get_coordinates(c) for c in channels]

    print "Sending seismic samples to `%s`..." % metricName

    # TODO: handle multiple stations
    network, station, location, channel = channels[0].split(".")
    while True:
      t = UTCDateTime(datetime.datetime.today())
      st = client.get_waveforms("IU", "ANMO", "00", "LHZ", t, t + 1)
      sample = st.traces[0].data[0]
      ts = int(time.time())
      sendSample(bus, metricName=metricName, value=sample, epochTimestamp=ts)
      print "Sent %f @ %d" % (sample, ts)
      sys.stdout.flush()
      time.sleep(5)
  else:
    print "Reading from file: {}".format(args.dataFile)
    dataFrame = pandas.read_csv(args.dataFile)
    rows, cols = dataFrame.shape
    for ts in range(rows):
      sample = dataFrame["seismic"][ts]
      sendSample(bus, metricName=metricName, value=sample, epochTimestamp=ts)
      print "Sent %f @ %d" % (sample, ts)
      sys.stdout.flush()
