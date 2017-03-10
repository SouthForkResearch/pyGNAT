# Name:         example_buffer.py
# Description:  Imports network shapefile to shapely geometry object, perform simple buffer,
#               export buffer back out to shapefile format.

import ogr
from shapely.geometry import *
import shapes as shp

# variables
in_shp = r"C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp"
out_shp = r"C:\JL\Testing\pyGNAT\NetworkFeatures\Out\Braids_buf50m.shp"

# open shapefile
print "Opening shapefile..."
strmList = []
strmShp = shp.Shapefile(in_shp)
strmList = strmShp.featuresToShapely()
# load stream reach shapes
multiLineStrings = MultiLineString([strm['geometry'] for strm in strmList])

# calculate buffer
print "Buffering stream..."
buf = multiLineStrings.buffer(50)

# write buffer polygon to disk
print "Exporting buffer to polygon shapefile..."
outShape = shp.Shapefile()
outShape.shapelyToFeatures(buf, out_shp, strmShp.spatialRef, ogr.wkbMultiPolygon)
