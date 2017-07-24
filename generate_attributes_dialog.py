# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GNATDialog
                                 A QGIS plugin
 Generate network attributes such as edge and node types, river kilometers,
 stream order, and branch identifiers.
                             -------------------
        begin                : 2017-07-18
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
from qgis.core import *
from qgis.gui import *
import qgis.utils
import networkx as nx
import network as net
import symbolizer as symbol


# constants
HELP_URL = "#"
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'generate_attributes_dialog.ui'))

class GenerateAttributesDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GenerateAttributesDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # Map functions to click events
        self.btnBrowseInput.clicked.connect(self.file_browser)
        self.chkNetworkErrors # TODO connect to checkbox

        self.btnBrowseOutput.clicked.connect(self.folder_browser)
        self.formFields = [self.txtInputNetwork, self.txtOutputFolder, self.txtResults]

        self.btnReset.clicked.connect(self.reset_form)
        self.btnRun.clicked.connect(self.calc_subnetwork_id)
        self.btnClose.clicked.connect(self.close)

        self.ExportToTxt.clicked.connect(self.export_to_txt)

        self.input_shp = ""
        self.output_folder = ""


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
        # TODO reset chkNetworkErrors


    def display_log_text(self, str_results):
        """
        Display results of processing to QT QTextEdit control for display.
        :param txtControl:
        """
        log_results = self.txtResults
        log_results.appendPlainText(str_results)


    def display_results_lyr(self):
        pass
        # TODO display and symbolize output by edge type


    def export_to_text(self):
        """
        Exports processing results to a text file
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


    def set_edge_types(G, network_id):
        """
        Determines edge types for a network graph. Intended for use with a loop
        so as to process each subnetwork separately
        :param network_id: Identifier value indicating a subnetwork
        :return: a graph (i.e. subnetwork) with edge types set
        """
        subnet_G = net.select_by_attribute(G, "NetworkID", network_id)
        net.add_attribute(subnet_G, "edge_type", "connector")
        outflow_G = net.get_outflow_edges(subnet_G, "edge_type")
        headwater_G = net.get_headwater_edges(subnet_G, "edge_type")
        braid_G = net.get_braid_edges(subnet_G, "edge_type")
        merge_G = nx.merge_subgraphs(subnet_G, outflow_G, headwater_G, braid_G)
        return merge_G


    # TODO main processing method
    def generate_attributes(self):
        """
        Main processing method, which imports a stream network shapefile (ideally
        with subnetworks already identified), converts it to a network graph,
        identifies edge types, node types, then calculates river kilometers from
        mouth, stream order, and branch ID.
        :return:
        """

        #PSEUDO-CODE
        # import shapefile to MultiDiGraph network
        if self.txtInputNetwork.text() != "" and self.txtOutputFolder.text() != "":
            start_string = time.ctime()
            start_time = time.time()
            self.display_log_txt("Processing started: {0}".format(start_string))
            QtCore.QCoreApplication.instance().processEvents()

            self.display_log_txt("Importing stream network shapefile...")
            QtCore.QCoreApplication.instance().processEvents()
            MG = net.import_shp(self.input_shp)

            # iterate through subnetworks
            dict_attrb = nx.get_edge_attributes(MG, "NetworkID")
            list_subnets = []
            if len(dict_attrb) > 0:
                network_id_list = net.get_unique_attrb(dict_attrb)
                for id in network_id_list:
                    edge_type_G = self.set_edge_types(MG, id)
                    # TODO add other processes here
                    # assign node types
                    # calculate river kilometers from mouth
                    # calculate stream order
                    # assign branch ID
                list_subnets.append(edge_type_G)

        # display output by edge type
        return