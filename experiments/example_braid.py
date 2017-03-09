# Name:         example_line2poly.py
# Description:  Imports network shapefile, converts to a polygon and
#               writes to a shapefile.

import ogr
from shapely.geometry import MultiPolygon, MultiLineString
from shapely.ops import polygonize
import shapes as shp

# variables
inShp = r"C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp"
outBraidPolyShp = r"C:\JL\Testing\pyGNAT\NetworkFeatures\Out\polyBraids.shp"
outBraidIntersectShp = r"C:\JL\Testing\pyGNAT\NetworkFeatures\Out\lineIntersectBraidPolys.shp"

# open shapefile
print "Opening shapefile..."
strmList, strmDriver, strmSpatialRef = shp.ogrWktToShapely(inShp, r"FType = '460' OR FType = '558'")
shplyStrm = MultiLineString(strmList)

# polygonize multiLineStrings object
strmPoly= MultiPolygon(list(polygonize(shplyStrm)))

# find multiLineStrings that intersect braid polygons
intersect = shplyStrm.intersection(strmPoly)

# write shapely objects to shapefiles
outBraidPoly = shp.Shapefile()
outBraidPoly.shapelyToFeatures(strmPoly, outBraidPolyShp, strmSpatialRef, ogr.wkbMultiPolygon)
outBraidIntersect = shp.Shapefile()
outBraidIntersect.shapelyToFeatures(intersect, outBraidIntersectShp, strmSpatialRef, ogr.wkbMultiLineString)

print "Process complete!"