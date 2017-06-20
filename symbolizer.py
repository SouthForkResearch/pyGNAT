import random
from osgeo import ogr
from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererCategoryV2, QgsCategorizedSymbolRendererV2


def symbolize_networkID(layer):
    # get network IDs from exported network shapefile
    index = layer.fieldNameIndex('NetworkID')
    id_values = layer.uniqueValues(index)

    categories = []
    for id in id_values:
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        symbol.setColor(QColor(random_color()))
        category = QgsRendererCategoryV2(id, symbol, str(id))
        categories.append(category)

    expression = "NetworkID"
    renderer = QgsCategorizedSymbolRendererV2(expression, categories)
    layer.setRendererV2(renderer)
    return


def random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)