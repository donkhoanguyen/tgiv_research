import osmnx as ox
import geopandas as gpd
import folium
import matplotlib.pyplot as plt

def get_road_network(city):
    """
    Get the map of any city outlined by drive-able paths. 
    Can view the result with matplotlib, save result in a shape file.
    """
    # Get the road network graph using OpenStreetMap data
    # 'network_type' argument is set to 'drive' to get the road network suitable for driving
    # 'simplify' argument is set to 'True' to simplify the road network
    G = ox.graph_from_place(city, network_type="drive", simplify=True)

    # Create a set to store unique road identifiers
    unique_roads = set()
    # Create a new graph to store the simplified road network
    G_simplified = G.copy()

    # Iterate over each road segment
    for u, v, key, data in G.edges(keys=True, data=True):
        # Check if the road segment is a duplicate
        if (v, u) in unique_roads:
            # Remove the duplicate road segment
            G_simplified.remove_edge(u, v, key)
        else:
            # Add the road segment to the set of unique roads
            unique_roads.add((u, v))
    
    # Update the graph with the simplified road network
    G = G_simplified
    
    # Project the graph from latitude-longitude coordinates to a local projection (in meters)
    G_proj = ox.project_graph(G)

    # Convert the projected graph to a GeoDataFrame
    # This function projects the graph to the UTM CRS for the UTM zone in which the graph's centroid lies
    _, edges = ox.graph_to_gdfs(G_proj) 

    return edges

# Get a list of points over the road map with a N distance between them
def select_points_on_road_network(roads, N=50):
    points = []
    # Iterate over each road
    
    for row in roads.itertuples(index=True, name='Road'):
        # Get the LineString object from the geometry
        linestring = row.geometry
        index = row.Index

        # Calculate the distance along the linestring and create points every 50 meters
        for distance in range(0, int(linestring.length), N):
            # Get the point on the road at the current position
            point = linestring.interpolate(distance)

            # Add the curent point to the list of points
            points.append([point, index])
    
    # Convert the list of points to a GeoDataFrame
    gdf_points = gpd.GeoDataFrame(points, columns=["geometry", "road_index"], geometry="geometry")

    # Set the same CRS as the road dataframes for the points dataframe
    gdf_points.set_crs(roads.crs, inplace=True)

    # Drop duplicate rows based on the geometry column
    gdf_points = gdf_points.drop_duplicates(subset=['geometry'])
    gdf_points = gdf_points.reset_index(drop=True)

    return gdf_points

# Define the city name
district = "Cau Giay District, Hanoi, Vietnam"

# Call the function and get the road network edges
road = get_road_network(district)
road_with_sample = select_points_on_road_network(road)
# Plot the road network
# plt.show()
# Plot the road network and the sampled points
# ax = road.plot(color="gray", linewidth=0.5)
# road_with_sample.plot(ax=ax, color="red", markersize=5)
# plt.show()


center_latitude, center_longitude = ox.geocode(district)

# Create a folium map centered at Cau Giay District
m = folium.Map(location=[center_latitude, center_longitude], zoom_start=14)

# Add road network edges to the map
# Plot the sampled points on the map
for point in road_with_sample['geometry']:
    folium.CircleMarker(location=[point.y, point.x], radius=2, color="red").add_to(m)

# Display the map
m