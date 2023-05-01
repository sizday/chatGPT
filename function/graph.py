import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64
plt.switch_backend('agg')


class RelationsGraph:
    def __init__(self, relations):
        self.relations = relations
        self.str_relation = str(relations)
        self.G = self.create_graph_from_list()
        self.image = self.save_visualise_graph()

    def merge(self, relations):
        self.relations += relations
        self.str_relation = str(relations)
        self.G = self.create_graph_from_list()
        self.image = self.save_visualise_graph()

    def create_graph_from_list(self):
        nodes = self.__get_all_notes()
        edges = self.__get_all_edges()
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        return G

    def __get_all_notes(self) -> list:
        nodes = []
        for first_entity, relation, second_entity in self.relations:
            nodes.append(first_entity)
            nodes.append(second_entity)

        nodes = list(set(nodes))
        return nodes

    def __get_all_edges(self) -> list:
        edges = []
        for first_entity, relation, second_entity in self.relations:
            clear_relation = relation.replace(str(second_entity), '').replace(str(first_entity), '')
            edges.append((first_entity, second_entity, {'relation': clear_relation}))

        return edges

    def save_visualise_graph(self):
        self.__visualize_graph()
        img = BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        base64_image = base64.b64encode(img.getvalue()).decode('utf8')
        base64_image_prefix = "data:image/png;base64,"
        return base64_image_prefix + base64_image

    def __visualize_graph(self):
        pos = nx.shell_layout(self.G)
        nx.draw(self.G, pos, with_labels=True)
        nx.draw_networkx_edge_labels(
            self.G,
            pos,
            edge_labels=self.__get_all_edge_labels(),
            font_color='red'
        )

    def __get_all_edge_labels(self):
        edge_labels = {}
        for edge in self.G.edges:
            edge_labels[edge] = self.G.edges[edge]['relation']
        return edge_labels
