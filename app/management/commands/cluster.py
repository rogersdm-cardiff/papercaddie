from sklearn import cluster
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.metrics.cluster import adjusted_rand_score
from django.core.management.base import BaseCommand, CommandError

from app.models import Paper, Person, PaperGroup

class Command(BaseCommand):

    def handle(self, *args, **options):
        persons = Person.objects.all()
        papers = Paper.objects.all()

        G = nx.Graph()

        for paper in papers:
            # name = '%s. %s' % (person.forename, person.surname)
            G.add_node(paper.id, title=paper.title)

        paper_list = list(papers)

        for paper_1 in papers:
            paper_list.remove(paper_1)
            print '%s/%s: %s' % (paper_1.id, len(paper_list), paper_1.title)
            for paper_2 in paper_list:
                if not paper_1 == paper_2:
                    for author_1 in paper_1.person_set.all():
                        for author_2 in paper_2.person_set.all():
                            if author_1 == author_2:
                                print 'adding edge!'
                                if G.has_edge(paper_1.id, paper_2.id):
                                    G[paper_1.id][paper_2.id]['weight'] += 1
                                else:
                                    G.add_edge(paper_1.id, paper_2.id, weight=1)

        isolates = list(nx.isolates(G))
        print isolates
        G.remove_nodes_from(isolates)

        graphs = list(nx.connected_component_subgraphs(G))

        for graph in graphs:
            nodes = list(graph.nodes())
            members = Paper.objects.filter(id__in=nodes)
            title = 'Group for Paper %s' % members[0].id
            graph_obj, created = PaperGroup.objects.get_or_create(title=title)

            if created:
                print 'Created %s' % title

                for member in members:
                    member.group = graph_obj
                    member.save()

        # pos = nx.spring_layout(G)

        # fig, ax = plt.subplots(figsize=(16,9))
        #
        # nx.draw_networkx_nodes(G, pos,
        #                        nodelist=ids,
        #                        node_size=500,
        #                        alpha=0.8,
        #                        ax=ax)
        #
        # nx.draw_networkx_edges(G, pos, alpha=0.5, ax=ax)

        # draw_communities(G, y_true, pos)

        # G = nx.star_graph(20)
        pos = nx.spring_layout(G)
        #colors = range(len(papers))
        nx.draw(G, pos, node_color='#A0CBE2', #edge_color=colors,
                width=4, edge_cmap=plt.cm.Blues, with_labels=False)
        plt.show()

        # nx.draw(G)
        # plt.savefig("path.png")

        print len(papers)