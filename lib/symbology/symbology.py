#   Name:           Symbology
#   Description:    Class for creating displaying shapefiles in QGIS Desktop. Derived from Matt's
#                   symbology class, developed for the RiverscapesToolbar
#                   https://github.com/Riverscapes/RiverscapesToolbar/blob/dev/RiverscapesToolbar/
#                   symbology/symbology.py
#   Authors:        Matt Reimer, matt@northarrowresearch.com
#                   Jesse Langdon, jesse@southforkresearch.org
#
#   Created:        5/23/2017
#   Revised:

import os
import sys
from raster import RasterPlugin
from vector import VectorPlugin
from qgis.core import QgsRasterLayer, QgsVectorLayer

class Symbology():

    _symbolizerspath = "symbolizers"

    # Library of "symbolizers" that are hot-loaded
    class _symbolizers:
        vector=[]
        raster=[]


    _loaded = False

    def __init__(self, force=False):
        if not self._loaded or force:
            Symbology.loadPlugins()


    @staticmethod
    def loadPlugins():
        """
        Load the symbology symbolizers into a library. Use whatever we can find. 
        This is a singleton pattern so you should only call it when the QGIS plugin loads.
        :return: 
        """

        pluginpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), Symbology._symbolizerspath)
        sys.path.insert(0, pluginpath)

        # Loop over all our symbolizers and add them to their respective libraries
        for f in os.listdir(pluginpath):
            fname, ext = os.path.splitext(f)
            if ext == '.py':
                mod = __import__(fname)
                if "RasterSymbolizer" in mod.__dict__:
                    Symbology._symbolizers.raster.append(mod.RasterSymbolizer)
                if "VectorSymbolizer" in mod.__dict__:
                    Symbology.__symbolizers.vector.append(mod.VectorSymbolizer)
        sys.path.pop(0)

        Symbology._loaded = True


    @staticmethod
    def symbolize(layer, symbology):
        """
        Here's where we choose the actual symbology and apply to the layer
        """

        if type(layer) is QgsRasterLayer:
            symbolizerInst = RasterPlugin(layer)
            library = Symbology._symbolizers.raster

        elif type(layer) is QgsVectorLayer:
            symbolizerInst = VectorPlugin(layer)
            library = Symbology._symbolizers.vector

        # Now that we've chosen our base class and our library (raster vs vector)
        # we monkey-patch the symbolize() method from the symbolizer class into
        # the rendered module.
        for plugin in library:
            if plugin.symbology == symbology:
                # monkey patch!
                # The __get__ sets the context and binds the appropriate "self" variable
                symbolizerInst.symbolize = plugin.symbolize.__get__(symbolizerInst)

        # Choose the default
        return symbolizerInst.apply()