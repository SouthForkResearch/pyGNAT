import random
from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererCategoryV2, QgsCategorizedSymbolRendererV2

class VectorSymbolizer():

    symbology = "Subnetworks"

    def symbolize(self, shp):

        # get network IDs from exported network shapefile
        from osgeo import ogr
        driver = ogr.GetDriverByName('ESRI Shapefiles')
        dataSrc = driver.Open(shp, 0)
        layer = dataSrc.GetLayer()
        index = layer.fieldNameIndex("NetworkID")
        id_values = layer.uniqueValues(index)


        categories = []
        for id in id_values:
            symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
            symbol.setColor(QColor(self.random_color()))
            category = QgsRendererCategoryV2(id, symbol, str(id))
            categories.append(category)

        expression = 'NetworkID'
        self.renderer = QgsCategorizedSymbolRendererV2(expression, categories)


    def random_color(self):
        return "#%06x" % random.randint(0, 0xFFFFFF)