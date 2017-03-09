# name:             shapes.py
# description:      Shapefile class which allows the creation, loading, and exporting of shapefiles.
# authors:          Matt Reimer (matt@northarrowresearch.org)
#                   Jesse Langdon (jesselangdon@gmail.com)
# sources:          https://github.com/NorthArrowResearch/pyGISExperiments/blob/master/metrics/shapefile_loader.py
# last revision:    3/6/2017
# version:          0.0.1
#

import os
import ogr
import json
from shapely.geometry import *
from shapely.wkt import loads

ogr.UseExceptions()

class Shapefile:

    def __init__(self, sFilename=None):
        self.driver = ogr.GetDriverByName("ESRI Shapefile")
        self.datasource = None
        if sFilename:
            self.load(sFilename)

    def load(self, sFilename):
        dataSource = self.driver.Open(sFilename, 0)
        self.layer = dataSource.GetLayer()
        self.spatialRef = self.layer.GetSpatialRef()

        self.getFieldDef()
        self.getFeatures()

    def create(self, sFilename, spatialRef=None, geoType=ogr.wkbMultiLineString):
        if os.path.exists(sFilename):
            self.driver.DeleteDataSource(sFilename)
        self.driver = None
        self.driver = ogr.GetDriverByName("ESRI Shapefile")
        self.datasource = self.driver.CreateDataSource(sFilename)
        self.layer = self.datasource.CreateLayer(sFilename, spatialRef, geom_type=geoType)

    def getFieldDef(self):
        self.fields = {}
        lyrDefn = self.layer.GetLayerDefn()
        for i in range(lyrDefn.GetFieldCount()):
            fieldName = lyrDefn.GetFieldDefn(i).GetName()
            fieldTypeCode = lyrDefn.GetFieldDefn(i).GetType()
            fieldType = lyrDefn.GetFieldDefn(i).GetFieldTypeName(fieldTypeCode)
            fieldWidth = lyrDefn.GetFieldDefn(i).GetWidth()
            GetPrecision = lyrDefn.GetFieldDefn(i).GetPrecision()

            self.fields[fieldName] = {
                'fieldName': fieldName,
                'fieldTypeCode': fieldTypeCode,
                'fieldType': fieldType,
                'fieldWidth': fieldWidth,
                'GetPrecision': GetPrecision
            }

    def getFeatures(self):

        self.features = []
        for feat in self.layer:
            self.features.append(feat)

    def featuresToShapely(self):
        if len(self.features) == 0:
            return

        feats = []
        for feat in self.features:
            featobj = json.loads(feat.ExportToJson())

            fields = {}
            for f in self.fields:
                fields[f] = feat.GetField(f)

            feats.append({
                'geometry': shape(featobj['geometry']),
                'fields': fields
            })
        return feats

    def shapelyToFeatures(self, shplyFeat, outShp, spatialRef, geoType):
        self.create(outShp, spatialRef, geoType)
        featureDefn = self.layer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        ogrJsonDump = ogr.CreateGeometryFromJson(json.dumps(mapping(shplyFeat)))
        outFeature.SetGeometry(ogrJsonDump)
        self.layer.CreateFeature(outFeature)

        return outFeature

def ogrWktToShapely(inShp, sql=''):
    shapely_objects = []
    feat_attrb = []
    srcDriver = ogr.GetDriverByName("ESRI Shapefile")
    srcShp = ogr.Open(inShp, 0)
    srcLyr = srcShp.GetLayer()
    spatialRef = srcLyr.GetSpatialRef()
    srcLyrDefn = srcLyr.GetLayerDefn()
    if sql != '':
        srcLyr.SetAttributeFilter(sql)
    # iterate over features, get geometry
    for feat in range(0, srcLyr.GetFeatureCount()):
        feature = srcLyr.GetFeature(feat)
        wktFeat = loads(feature.geometry().ExportToWkt())
        shapely_objects.append(wktFeat)
        # iterate through fields, get feature names
        for field in range(0, srcLyrDefn.GetFieldCount()):
            fieldDefn = srcLyrDefn.GetFieldDefn(field)
            fieldName = fieldDefn.GetName()
            feat_attrb.append(fieldName)

    return shapely_objects, srcDriver, spatialRef