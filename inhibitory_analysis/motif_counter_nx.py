# file to use in HPC to count wholeNet_motifs
import pandas as pd
import numpy as np
import networkx as nx
import pickle

syn_table = pd.read_csv('connections_no_threshold.csv')

# PROCESSING
# Find all unique cell ids in both the pre and post columns
cellids =  np.unique(syn_table[["pre_root_id", "post_root_id"]])

# Create a dictionary that maps cell ids to index id values
nid2cid = {i: cid for i, cid in enumerate(cellids)}

# Create a dictionary that maps index id values to cell ids, may not be needed
cid2nid = {cid: i for i, cid in enumerate(cellids)}


# Add the index id values to the syn_table for pre and post columns
syn_table["pre_nid"] = pd.Series([cid2nid[cid] for cid in syn_table["pre_root_id"]], 
		index=syn_table.index)
syn_table["post_nid"] = pd.Series([cid2nid[cid] for cid in syn_table["post_root_id"]], 
		index=syn_table.index)

# Limit to pre and post columns
syn_table_limit = syn_table[["pre_nid", "post_nid"]]

# Graph processing
G = nx.DiGraph()
# Add the edges to the graph from dataframe
G.add_edges_from(syn_table_limit.values)

triads = nx.triads_by_type(G)

with open('triads_dict.pkl', 'wb') as file:
    pickle.dump(triads, file)

