# print(__doc__)

# Script to use scikit-learn for spectral co-clustering. Run this
# after generating the analysis datasets from experimental data

import numpy as np
from matplotlib import pyplot as plt
import pymongo
from pymongo import MongoClient

from sklearn.cluster.bicluster import SpectralCoclustering
# from sklearn.metrics import consensus_score

client = MongoClient('localhost', 3001)
db = client.meteor

events = db['analysis.events']
datastream = db['analysis.datastream']

# We expect about this many events from Pablo
n_clusters = 100

# Build array of relationships between events and tweets

n_rows = datastream.find().count()
n_cols = events.find().count()
shape = (n_rows, n_cols)

# Should we really use float64 here?
data = np.ones(shape, dtype=np.float64) * 0.001

# Map tweets to a contiguous list, for now
row_lookup = {}
for i, tweet in enumerate(datastream.find().sort('num', pymongo.ASCENDING)):
    row_lookup[tweet['num']] = i

for j, event in enumerate(events.find()):
    sources = event['sources']    
    # Skip empty lists
    if not sources:
        continue
    
    # TODO hack: skip very long lists
    if len(sources) > 50:
        continue

    # All events have numbered tweets
    rowSelector = np.array([row_lookup[source] for source in sources])
    data[rowSelector, j] = 1    

plt.matshow(data, cmap=plt.cm.Blues)
plt.title("Original dataset")

model = SpectralCoclustering(n_clusters=n_clusters, random_state=0)
model.fit(data)

fit_data = data[np.argsort(model.row_labels_)]
fit_data = fit_data[:, np.argsort(model.column_labels_)]

plt.matshow(fit_data, cmap=plt.cm.Blues)
plt.title("After biclustering; rearranged")

avg_data = np.copy(data)

# Compute average value in each co-cluster for display purposes
for c in range(n_clusters):
    for d in range(n_clusters):                       
        row_ind = np.nonzero(model.rows_[c])
        col_ind = np.nonzero(model.columns_[d])
        # print row_ind, col_ind

        row_sel = np.tile(row_ind, (col_ind[0].size, 1))
        col_sel = np.tile(col_ind, (row_ind[0].size, 1)).transpose()
        # print row_sel, col_sel
           
        avg_data[row_sel, col_sel] = np.average(data[row_sel, col_sel])

avg_data = avg_data[np.argsort(model.row_labels_)]
avg_data = avg_data[:, np.argsort(model.column_labels_)]

plt.matshow(avg_data, cmap=plt.cm.Blues)
plt.title("Cluster intensity of rearranged data")

plt.show()
