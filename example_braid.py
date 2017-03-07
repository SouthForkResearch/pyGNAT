# Name:         example_line2poly.py
# Description:  Imports network shapefile, converts to a polygon and
#               writes to a shapefile.

import ogr
from shapely.geometry import MultiPolygon, MultiLineString
from shapely.ops import polygonize
from shapely.wkt import loads
import shapes as shp

# variables
inShp = r"C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp"
outBraidPolyShp = r"C:\JL\Testing\pyGNAT\NetworkFeatures\Out\polyBraids.shp"
outBraidIntersectShp = r"C:\JL\Testing\pyGNAT\NetworkFeatures\Out\lineIntersectBraidPolys.shp"

# open shapefile
print "Opening shapefile..."
driver = ogr.GetDriverByName("ESRI Shapefile")
srcShp = driver.Open(inShp, 0)
srcLayer = srcShp.GetLayer()
spatialRef = srcLayer.GetSpatialRef()

# select only NHD stream feature and connector types, no canals
strmList = []
srcLayer.SetAttributeFilter("FType = '460' OR FType = '558'")
for f in range(0, srcLayer.GetFeatureCount()):
    strmFeat = srcLayer.GetFeature(f)
    wktFeat = loads(strmFeat.geometry().ExportToWkt())
    strmList.append(wktFeat)
shplyStrm = MultiLineString([strm for strm in strmList])

# polygonize multiLineStrings object
strmPoly = MultiPolygon(list(polygonize(shplyStrm)))

# find multiLineStrings that intersect braid polygons
intersect = shplyStrm.intersection(strmPoly)

# write shapely objects to shapefiles
outBraidPoly = shp.Shapefile()
outBraidPoly.shapelyToFeatures(strmPoly, outBraidPolyShp, spatialRef, ogr.wkbMultiPolygon)
outBraidIntersect = shp.Shapefile()
outBraidIntersect.shapelyToFeatures(intersect, outBraidIntersectShp, spatialRef, ogr.wkbMultiLineString)

print "Process complete!"