
# this is python code that read pubtator output file (.._PubtaTor.tsv) in which "MTBLS", id MTBLS id,"TermID" is the TermID which potentially 
# contain MESH ID(MSESH:***) and species id (integer).
# This filecollect MESH ID for each MTBLS ID and MTBLS will have list of MESH ID.

# first, read the file and make a dictionary with MTBLS id as key and list of MESH ID as value.
# second, read the file and make a dictionary with MESH ID as key and list of MTBLS id as value.

# read "20231017_PubTator.tsv"

import itertools
import networkx as nx

dict_MTBLSID_vs_list_MeshID = {}
dict_MTBLSID_vs_list_speciesID = {}

import csv

with open('20231017_PubTator.tsv', 'r') as file:
    reader = csv.DictReader(file, delimiter='\t')
    for row in reader:
        mtbls_id = row['MTBLS']
        term_id = row['TermID']

        # it term_id starts with "MESH", then it is MESH ID
        if term_id.startswith("MESH"):
            # if mtbls_id is already in the dictionary, then append the term_id to the list
            if mtbls_id in dict_MTBLSID_vs_list_MeshID:
                dict_MTBLSID_vs_list_MeshID[mtbls_id].append(term_id)
            # if mtbls_id is not in the dictionary, then create a new list with term_id
            else:
                dict_MTBLSID_vs_list_MeshID[mtbls_id] = [term_id]
        
        #if term id stars with not "MESH", but integer, then it is species id
        elif term_id.isdigit():
            # if mtbls_id is already in the dictionary, then append the term_id to the list
            if mtbls_id in dict_MTBLSID_vs_list_speciesID:
                dict_MTBLSID_vs_list_speciesID[mtbls_id].append(term_id)
            # if mtbls_id is not in the dictionary, then create a new list with term_id
            else:
                dict_MTBLSID_vs_list_speciesID[mtbls_id] = [term_id]
        
        
# just show contents


for mtbls_id in dict_MTBLSID_vs_list_MeshID:
    print(mtbls_id, dict_MTBLSID_vs_list_MeshID[mtbls_id])





# func to calculate Jaccard coef 
def calculate_jaccard(set1, set2):
    intersection = len(set(set1).intersection(set2))
    union = len(set(set1).union(set2))
    return intersection / union if union != 0 else 0


# ノードとエッジのリストを準備
nodes = list(dict_MTBLSID_vs_list_MeshID.keys())
edges = []

# 全論文のペアに対してJaccard係数を計算し、エッジリストに追加
for (mtbls_id1, mesh_ids1), (mtbls_id2, mesh_ids2) in itertools.combinations(dict_MTBLSID_vs_list_MeshID.items(), 2):
    jaccard_score = calculate_jaccard(set(mesh_ids1), set(mesh_ids2))  # convert list to set.
    if jaccard_score > 0.2:  # Jaccard係数が0より大きい場合のみエッジを追加
        edges.append((mtbls_id1, mtbls_id2, jaccard_score))
        
        

# ノードとエッジのリストをCSVファイルとして出力
with open('nodes.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Node"])
    for node in nodes:
        writer.writerow([node])

with open('edges.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Source", "Target", "Weight"])
    for edge in edges:
        writer.writerow(edge)


# NetworkXグラフの作成
G_raw = nx.Graph()
G_raw.add_nodes_from(nodes)
G_raw.add_weighted_edges_from(edges)


num_nodes = G_raw.number_of_nodes()
num_edges = G_raw.number_of_edges()

print("Number of nodes (G_raw):", num_nodes)
print("Number of edges (G_raw):", num_edges)

#import plotly.graph_objects as go


# Get positions for the nodes in G_raw
print("performing spring layout")
pos = nx.spring_layout(G_raw)


import matplotlib.pyplot as plt
# Draw the graph
nx.draw(G_raw, node_size=25, with_labels=False)
plt.show()






# community detection ------------
print("community detection------------")
from networkx.algorithms import community
from networkx.algorithms.community import girvan_newman
import community as community_louvain
# perform community detection using louvain algorithm


# set community detection resolution:  high: more small communityies
comm_detection_resolution = 0.4
print ("resolution:" , comm_detection_resolution)
communities = community_louvain.best_partition(G_raw, resolution = comm_detection_resolution)

# Get the number of communities
num_communities = len(set(communities.values()))
print("Number of communities:", num_communities)

# 新しいグラフを作成し、エッジリストを初期化
G_new = nx.Graph()
list_inner_community_edges = []
list_inter_community_edges = []

# 新しいグラフを作成し、内部コミュニティエッジを追加
G_new = nx.Graph()
for node1 in G_raw.nodes():
    for node2 in G_raw.nodes():
        if communities[node1] == communities[node2] and G_raw.has_edge(node1, node2):
            G_new.add_edge(node1, node2)



num_nodes = G_new.number_of_nodes()
num_edges = G_new.number_of_edges()

print("Number of nodes (G_new):", num_nodes)
print("Number of edges (G_new):", num_edges)

# create list of edges within communities
for edge in G_new.edges():
    list_inner_community_edges.append(edge)

# create list of edges between communities
for edge in G_raw.edges():
    if edge not in list_inner_community_edges:
        list_inter_community_edges.append(edge)
        
        


# 可視化
pos = nx.spring_layout(G_new)
nx.draw_networkx_edges(G_new, pos, alpha=0.5)
nx.draw_networkx_nodes(G_new, pos, node_size=25, cmap=plt.cm.jet)
#plt.title("Network Visualization with Community Structure")
plt.show()