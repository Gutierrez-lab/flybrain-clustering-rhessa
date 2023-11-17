import os
# import sys
import pandas as pd
import numpy as np
import argparse
import logging
from neuprint import Client, fetch_neurons

# process commandline args
parser = argparse.ArgumentParser()
parser.add_argument('hemibrain_version',
                    help="Hemibrain version (format as 1.x, no preceding 'v'). Will attempt to read hemibrain/exported-traced-adjacencies-vXX")
parser.add_argument('--path', default="ovi_combined/clustering_v", help="Explicit path; using this ignores positional argument")
parser.add_argument('--neuron_csv', default="ovi_comb_full_key.txt", help="Name of neuron csv, bodyIds (key.txt)")
parser.add_argument('--edge_csv', default="ovi_comb_full_formatted.txt", help="Name of edge csv, if different from traced-total-connections.csv")
parser.add_argument('--cluster_csv', default="cluster_info.xlsx", help="Name of edge csv, if different from default")
parser.add_argument('--cluster_dir', default='ovi_combined/clustering_v', help="Directory with cluster info. Gets version appended")
parser.add_argument('--output_dir', default="ovi_combined/preprocessed-v", help="Output directory, which will have version appended. Created if doesn't exist.")
parser.add_argument('--loglevel', choices=["debug", "info", "warning", "error", "critical"], default="info", help="Level of verbosity")
parser.add_argument('--auth_file', default="flybrain.auth.txt", help="File with auth token")
parser.add_argument('-f', '--force', action='store_true', help="Overwrite output files if they already exist")
args = parser.parse_args()

# configure logging
loglevel = args.loglevel.upper()
logging.basicConfig(format="%(asctime)s  %(module)s> %(levelname)s: %(message)s", datefmt="%Y %m %d %H:%M:%S", level=getattr(logging, loglevel.upper()))

# locate all the relevant files
path = args.path + args.hemibrain_version
cluster_dir = args.cluster_dir + args.hemibrain_version
output_dir = args.output_dir + args.hemibrain_version
if not os.path.isdir(output_dir):
    logging.info("Creating path %s", output_dir)
    os.mkdir(output_dir)

# neuron_csv is bodyIDs and key, edge_csv is the edge_list
neuron_csv = os.path.join(path, args.neuron_csv)
edge_csv = os.path.join(path, args.edge_csv)
cluster_info = os.path.join(path, args.cluster_csv)


output_node_csv = os.path.join(output_dir, "preprocessed_nodes.csv")
output_uedge_csv = os.path.join(output_dir, "preprocessed_undirected_edges.csv")
output_dedge_csv = os.path.join(output_dir, "preprocessed_directed_edges.csv")

# check that output doesn't exist, or that overwrite option is set
if not args.force and any([os.path.isfile(f) for f in [output_node_csv, output_uedge_csv, output_dedge_csv]]):
    logging.warning("Found existing output file(s):")
    for f in [output_node_csv, output_uedge_csv, output_dedge_csv]:
        if os.path.isfile(f):
            print(f)
    logging.warning("Force overwriting with -f, or specifiy output with --output_dir")
    exit(1)

# Connect to Janelia
auth_token_file = open(args.auth_file, 'r')
auth_token = next(auth_token_file).strip()
np_client = Client('neuprint.janelia.org', dataset='hemibrain:v' + args.hemibrain_version, token=auth_token)
logging.info('Connected to neuprint; client version %s', np_client.fetch_version())


logging.debug("path = %s", path)
logging.debug("cluster_dir = %s", cluster_dir)

logging.info("Attempting to read neuron csv with pandas: %s", neuron_csv)

cluster_df = pd.read_excel(cluster_info)
local_df = pd.read_csv(neuron_csv, delimiter=' ', header=None).rename(columns={0: "bodyId", 1:" key"})
local_df = pd.concat([local_df, cluster_df],axis=1).rename(columns={0:"0.0"})

logging.info("Fetching neuron datafrom from neuprint")
neuprint_df, conn_df = fetch_neurons(local_df["bodyId"])
neuprint_df.fillna(value={"type": "None", "instance": "None"}, inplace=True)
print(neuprint_df.head())
print()

logging.info("Merging dataframes")
FB_node_df = pd.merge(local_df, neuprint_df, on="bodyId").rename(columns={"bodyId": "id", "type": "celltype"}).set_index("id")
print(FB_node_df.head())
print()

logging.info("Writing preprocessed node df to %s", output_node_csv)
FB_node_df.to_csv(output_node_csv)

logging.info("Loading edges and renaming columns from %s", edge_csv)
edge_df = pd.read_csv(edge_csv, delimiter=' ', header=None).rename(columns={0:"node1", 1:"node2", 2:"weight"})
print(edge_df.head())
print()

edge_df[["node1", "node2"]] = np.sort(edge_df[["node1", "node2"]])
if np.any(edge_df["node1"] > edge_df["node2"]):
    logging.error("Failed to sort nodes properly! Throwing up hands in frustration...")
    exit(1)

logging.info("Converting to undirected graph")
grouped_edges = edge_df.groupby(["node1", "node2"]).agg(total_weight=pd.NamedAgg(column="weight", aggfunc=sum))
edge_df = grouped_edges.reset_index()
print(edge_df.head())
print()

logging.info("Writing to %s", output_uedge_csv)
edge_df.to_csv(output_uedge_csv)
