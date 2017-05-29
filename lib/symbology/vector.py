from qgis.core import QgsSymbolV2, QgsSingleSymbolRendererV2, QgsSimpleLineSymbolLayerV2

class VectorPlugin():

    def __init__(self, layer):

        self.layer = layer
        self.provider = layer.dataProvider()
        extent = layer.extent
        self.renderer = None

    def apply(self):
        """
        Applies the previously defined ramps and shaders
        :return: 
        """
        self.symbolize()

        # Assign renderer to layer
        self.layer.setRendererV2(self.renderer)

        # Trigger repaint with new style
        self.layer.triggerRepaint()

    def symbolize(self):

        # create a new single symbol renderer
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        self.renderer = QgsSingleSymbolRendererV2(symbol)

        # create a new simple line symbol layer
        properties = {'width': 0.5, 'color': 'gray'}
        symbol_layer = QgsSimpleLineSymbolLayerV2.create(properties)

        #assign symbol layer to the symbol
        if self.renderer.symbols()[0] is not None:
            self.renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)