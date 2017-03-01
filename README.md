# pyGNAT
Geomorphic network analysis toolbox, redesigned using FOSS python libraries.

The [NetworkFeatures.zip](https://github.com/SouthForkResearch/pyGNAT/raw/master/NetworkFeatures.zip) file contains a series of shapefiles:
- `NHD_Braids.shp` : includes simple and complex braids.
- `NHD_Canals.shp` : canal features are designated using the FCode attribute field, where FType = 336
- `NHD_Disconnected.shp` : valid disconnections vs errors can be found with the "JL_Notes" attribute field
- `NHD_Flow_Direction.shp` : stream features with incorrect flow direction can be found with the "JL_Notes" field.
- `NHD_Waterbody_connectors.shp` : stream features that are "connectors" (i.e. inside a waterbody polygon) are found using FCode attribute field, where FCode = 55800
- `NHD_Waterbody_polygons.shp` : water bodies as polygons.
