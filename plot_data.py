import argparse
import numpy as np
import repository

import htmengine.repository.queries as queries
from pylab import *

parser = argparse.ArgumentParser()
parser.add_argument("--metric", default="old",
  choices=["stream1","stream2", "old"], help="File of past data to use")
args = parser.parse_args()

metricIDs = {
    "stream1": "416fdf44e93847ff8682340a4214069a",
    "stream2": "a83c3d89d08a47f8b234aaf9d55b75b7",
    "old": "8c497721b7d442d7b8a9f904ee3bf456"
}

print "Getting data for metric: {}".format(args.metric)

engineFactory = repository.engineFactory()

metricData = list(queries.getMetricData(engineFactory, metricIDs[args.metric]))
#id, *, time, data, raw anomaly, anomaly score
anomaly = np.array([d[5] for d in metricData])
data = np.array([d[3] for d in metricData])

data = data - np.mean(data)
anomaly = np.array([a if a is not None else np.nan for a in anomaly])
anomaly *= np.max(np.abs(data))

print "Plotting"

plot(range(1, len(data) + 1), data)
plot(range(1, len(data) + 1), anomaly)
show()
