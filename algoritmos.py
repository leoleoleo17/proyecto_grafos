import csv
import networkx as nx
import matplotlib.pyplot as plt
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

'''
Graph Recommender: Clase que construye 2 tipos de grafos: La red entre los usuarios  y la red de artistas por géneros. (No es necesario hacer el grafo de cada usuario porque el algoritmo de recomendación solo itera por los artistas)
Input: doc, el path del archivo .csv en donde cada fila representa a un usuario y cada columna representa el top de los usuarios en orden descendente
Output: guarda en memoria los 2 grafos (todavía no se me ocurre como, de pronto usar pickle no je)
'''
class Graph_Recommender():

    def __init__(self, doc) -> None:
        self.doc = doc
        self.artistas = {} #Aquí se van a guardar un diccionario con llave el nombre del artista en mayúsculas, su código de Spotify y los géneros asociados a él
        self.usuarios = [] #Aquí se guardan los usuarios con su top 10 asociado a ellos en un diccionario
        self.grafo_usuarios = None

    def crear_usuarios(self):
        with open(self.doc) as d:
            reader = csv.reader(d, delimiter=';')
            for u in reader:
                usuario = {}
                for i,a in enumerate(u):
                    usuario[i+1] = a
                    self.artistas[a]=[]
                self.usuarios.append(usuario)

    def get_artist_genres(self,artist_name):
        # Set up Spotipy client credentials
        client_id = '4417bca2fc0f405aa211b519e067bbaf'
        client_secret = '9d53090efda44e968a6d4d5f5166ca36'
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        # Search for the artist
        results = sp.search(q=artist_name, type='artist', limit=1)
        if 'artists' in results and 'items' in results['artists'] and len(results['artists']['items']) > 0:
            artist = results['artists']['items'][0]
            return artist['genres']
        else:
            return []
        
    def fetch_genero_artistas(self):
        cont=0
        cont2=0
        for artista in self.artistas.keys():
            
            self.artistas[artista]=self.get_artist_genres(artista)
        
        #PARA VER ARTISTAS SIN GENERO
        for artista in self.artistas.keys():
            if self.artistas[artista]==[]:
                print(artista, self.artistas[artista])
                cont+=1
            cont2+=1
        print(cont, "/", cont2)

    def crear_grafo_usuarios(self):
        G = nx.Graph()
        #Crear los nodos numerados y con atributo el dict con el top de artistas
        for i,u in enumerate(self.usuarios):
            G.add_node(i,top = u, min = [])
        #Crear las aristas entre usuario según la métrica de afinidad entre usuarios
        for u1 in range(len(self.usuarios)):
            u1_min = {}
            for u2 in range(len(self.usuarios)):
                if u1 != u2:
                    #Calcula el common artists entre u1 y u2
                    artists_u1 = G.nodes[u1]['top'].values()
                    artists_u2 = G.nodes[u2]['top'].values()
                    a_u1 = set([i for i in artists_u1])
                    a_u2 = set([i for i in artists_u2])
                    CA = len(a_u1.intersection(a_u2))
                    if CA != 0: #No tiene sentido buscar el common position cuando no comparten artistas
                        CP = 0
                        for u1_a, u2_a in zip(artists_u1,artists_u2):
                            if u2_a == u1_a:
                                CP +=1
                        puntaje_u1_u2 = 1/(4*CA + 6*CP)
                    else:
                        puntaje_u1_u2 = 2 #No comparten artistas

                    #Guarda el usuario y el peso si es de los 6 con menor afinidad
                    if puntaje_u1_u2 !=2:
                        if len(u1_min) < 6: 
                            u1_min[u2] = puntaje_u1_u2
                        else:
                            if puntaje_u1_u2 < min(u1_min.values()):
                                mx = max(u1_min, key = u1_min.get())
                                del u1_min[mx]
                                u1_min[u2] = puntaje_u1_u2

            #Crea las aristas con los nodos con afinidad mínima
            for user in u1_min:
                G.add_edge(u1, user)
        nx.draw_networkx(G, pos = nx.spiral_layout(G))
        plt.show()


g = Graph_Recommender('proyecto_grafos/respuestas.csv')
g.crear_usuarios()
g.fetch_genero_artistas()
g.crear_grafo_usuarios()
