import requests
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry

# define the URL for the geocoding service (e.g. Nominatim, Google, or Mapbox).
url = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
access_token = "&access_token=YOUR_API_KEY"

# optional mapbox parameters
language = "de"
limit = "2"
# types options are country, region, postcode, district, place, locality, neighborhood, address, and poi
types = "adress"

# define the file with the addresses to be geocoded
address_file_path = "path to .csv file"

# empty list and layer for results 
features = []
layer = QgsVectorLayer("Point?crs=epsg:25832", "Geocodierte Adressen", "memory")
pr = layer.dataProvider()
pr.addAttributes([QgsField("Adressen", QVariant.String), QgsField("Adressen_Mapbox", QVariant.String)])
layer.updateFields() 

# open the file with the addresses and read in each line
with open(address_file_path, "r") as f:
    for line in f:
        # removes line breaks and commas
        line = line.strip()
        line = line.replace(",","")
        # replaces white spaces with mapbox specification
        query = line.replace(" ", "%20")
        # creats the URL
        full_url = url + query + ".json?limit=" + limit + "?language=" + language + "?types=" + types + access_token
        response = requests.get(full_url)
        data = response.json()
        # checks results
        if data:
            # selects the first result
            print(line)
            print(data['features'][0]['geometry']['coordinates'][0])
            print(data['features'][0]['geometry']['coordinates'][1])

            lat = data['features'][0]['geometry']['coordinates'][0]
            lon = data['features'][0]['geometry']['coordinates'][1]
            
            # transform crs
            sourceCrs = QgsCoordinateReferenceSystem(4326)
            destCrs = QgsCoordinateReferenceSystem(25832)
            tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
            
            point = QgsGeometry.fromPointXY(tr.transform(QgsPointXY(float(lat), float(lon))))
            # creates a feature with adress attribute
            feature = QgsFeature()
            feature.setGeometry(point)
            feature.setAttributes([line, data['features'][0]['place_name']])

            features.append(feature)

layer.dataProvider().addFeatures(features)
layer.updateExtents() 

# add layer to map
QgsProject.instance().addMapLayer(layer)
