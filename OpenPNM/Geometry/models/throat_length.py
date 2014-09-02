r"""
===============================================================================
Submodule -- throat_length
===============================================================================

"""
import scipy as _sp

def straight(network,
             geometry,
             pore_diameter='pore.diameter',
             **kwargs):
    r"""
    Calculate throat length 
    """
    #Initialize throat_property['length']
    throats = network.throats(geometry.name)
    pore1 = network['throat.conns'][:,0]
    pore2 = network['throat.conns'][:,1]
    C1 = network['pore.coords'][pore1]
    C2 = network['pore.coords'][pore2]
    E = _sp.sqrt(_sp.sum((C1-C2)**2,axis=1))  #Euclidean distance between pores
    D1 = network[pore_diameter][pore1]
    D2 = network[pore_diameter][pore2]
    value = E-(D1+D2)/2
    value = value[throats]
    if _sp.any(value<0):
        geometry._logger.warning('Negative throat lengths are calculated. Arbitrary positive length assigned (1e9 meters)')
        Ts = _sp.where(value<0)[0]
        value[Ts] = 1e-9
    return value
        
def voronoi(network,
            geometry,
            **kwargs):
    r"""
    Calculate the centre to centre distance from centroid of pore1 to centroid of throat to centroid of pore2
    This is tricky as connections are defined at network level but centroids are stored on geometry.
    The pore and throat map relates the geometry index to the network index but we must look up the index of the map
    to go back to geometry index of the connected pores.
    This will probably break down when a throat connects two different geometries 
    """
    throats = geometry['throat.map']
    connections = network['throat.conns'][throats]
    net_pore1 = connections[:,0]
    net_pore2 = connections[:,1]
    geom_pore1 = []
    geom_pore2 = []
    for net_pore in net_pore1:
        geom_pore1.append(geometry['pore.map'].tolist().index(net_pore))
    for net_pore in net_pore2:
        geom_pore2.append(geometry['pore.map'].tolist().index(net_pore))
    
    pore_centroids = geometry['pore.centroid']
    throat_centroids = geometry['throat.centroid']
    v1 = throat_centroids-pore_centroids[geom_pore1]
    v2 = throat_centroids-pore_centroids[geom_pore2]
    value = _sp.ndarray(len(connections))
    for i in range(len(connections)):
        value[i] = _sp.linalg.norm(v1[i])+_sp.linalg.norm(v2[i])
    return value
