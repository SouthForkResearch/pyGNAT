# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GNATDialog
                                 A QGIS plugin
 Build network identifiers for subnetworks in a stream network dataset.
                             -------------------
        begin                : 2017-04-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by South Fork Research, Inc.
        email                : jesse@southforkresearch.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import time
from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
import network as network
import symbolizer as symbol
from qgis.core import *
from qgis.gui import *
import qgis.utils


# constants
HELP_URL = "#"
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'build_network_dialog_base.ui'))


class BuildNetworkDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(BuildNetworkDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # Map functions to click events
        self.btnBrowseInput.clicked.connect(self.file_browser)
        self.btnBrowseOutput.clicked.connect(self.folder_browser)
        self.btnRun.clicked.connect(self.calc_subnetwork_id)

        self.formFields = [self.txtInputNetwork, self.txtOutputFolder, self.txtResults]
        self.btnReset.clicked.connect(self.reset_form)

        self.btnExportToTxt.clicked.connect(self.export_to_txt)
        self.btnDisplayResults.clicked.connect(self.display_results_lyr)
        self.btnClose.clicked.connect(self.close)

        self.input_shp = ""
        self.output_folder =""


    def file_browser(self):
        """
        Set QT QLineEdit control to user-specified file name.
        :param txtControl: name of the QLineEdit control
        """
        file_path = QtGui.QFileDialog.getOpenFileName(self, "Open Shapefile", "C:\\", "Shapefile (*.shp)")
        win_path = QDir.toNativeSeparators(file_path)
        self.input_shp = str(win_path)
        self.txtInputNetwork.setText(self.input_shp)


    def folder_browser(self):
        """
        Set QT QLineEdit control to user-specified folder name.
        :param txtControl: name of the QLineEdit control
        """
        self.output_folder = QtGui.QFileDialog.getExistingDirectory(self, "Select Output Folder", "C:\\", QtGui.QFileDialog.ShowDirsOnly)
        self.txtOutputFolder.setText(self.output_folder)


    def reset_form(self):
        for field in self.formFields:
            field.clear()
        if hasattr(self, "input_shp"):
            del self.input_shp
        if hasattr(self, "output_folder"):
            del self.output_folder


    def display_log_txt(self, str_results):
        """
        Display results of processing to QT QTextEdit control for display.
        :param txtControl:
        """
        log_results = self.txtResults
        log_results.appendPlainText(str_results)


    def display_results_lyr(self):
        """
        Display processed network shapefile, with a random
        :return:
        """
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "network_lines":
                QgsMapLayerRegistry.instance().removeMapLayer(lyr)
        edge_name = "network_lines.shp"
        out_edge_shp = self.output_folder + "\\" + edge_name
        output_layer = QgsVectorLayer(out_edge_shp, "network_lines", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(output_layer)
        symbol.symbolize_networkID(output_layer)
        qgis.utils.iface.mapCanvas().refresh()


    def export_to_txt(self):
        """
        Exports processing results to a text file.
        :return:
        """
        from qgis.gui import QgsMessageBar
        file_name = QtGui.QFileDialog.getSaveFileName(self,
                                                      'Save Results as Text File',
                                                      "C:\\",
                                                      "Text (*.txt)")
        with open(file_name, 'w') as file_export:
            file_export.write(str(self.txtResults.toPlainText()))

        qgis.utils.iface.messageBar().pushMessage("Info", "Processing results saved!",
                                       level=QgsMessageBar.INFO)


    def closeEvent(self, event):
        self.reset_form()


    def calc_subnetwork_id(self):
        """
        Main processing method, which imports a stream network shapefile,
        converts it to a networkx graph, finds sub-graphs, generates a unique
        identifier for each sub-graph, then converts the graph back to a
        shapefile with a new NetworkID attribute.
        :return:
        """
        if self.txtInputNetwork.text() != "" and self.txtOutputFolder.text() != "":
            start_string = time.ctime()
            start_time = time.time()
            self.completed = 0
            self.display_log_txt("Processing started: {0}".format(start_string))
            QtCore.QCoreApplication.instance().processEvents()

            self.display_log_txt("Importing stream network shapefile...")
            QtCore.QCoreApplication.instance().processEvents()
            DG = network.import_shp(self.input_shp)

            self.display_log_txt("Finding subnetworks...")
            list_SG = network.get_subgraphs(DG)
            QtCore.QCoreApplication.instance().processEvents()

            self.display_log_txt("Calculating subnetwork IDs...")
            UG = network.calc_network_id(list_SG)
            QtCore.QCoreApplication.instance().processEvents()

            self.display_log_txt("Writing output shapefiles...")
            network.export_shp(UG, self.input_shp, self.output_folder)
            QtCore.QCoreApplication.instance().processEvents()

            stop_string = time.ctime()
            stop_time = time.time()
            total_time = round(((stop_time - start_time)/60), 2)
            self.display_log_txt("Processing completed: {0}".format(stop_string))
            self.display_log_txt("Total processing time: {0} minutes".format(total_time))
            self.display_log_txt("--------------------------\n")

            # Display results as text and layers in QGIS TOC
            list_results = network.get_graph_attributes(UG, "NetworkID")
            for result in list_results:
                self.display_log_txt(result)
            # if self.inputCheck():
            #     QtCore.QCoreApplication.instance().processEvents()
        elif self.txtInputNetwork.text() == "":
            qgis.utils.iface.messageBar().pushMessage("Error", "Shapefile required",
                                                      level=QgsMessageBar.CRITICAL)
        elif self.txtOutputFolder.text() == "":
            qgis.utils.iface.messageBar().pushMessage("Error", "Select output directory",
                                                      level=QgsMessageBar.CRITICAL)