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
from PyQt4.QtCore import Qt
import lib.network as network
from qgis.core import *
from qgis.gui import *


# constants
HELP_URL = "#"
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'build_network_dialog_base.ui'))


class GNATDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GNATDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # Map functions to click events
        self.btnBrowseInput.clicked.connect(lambda: self.file_browser(self.txtInputNetwork))
        self.btnBrowseOutput.clicked.connect(lambda: self.folder_browser(self.txtOutputFolder))
        self.btnRun.clicked.connect(self.calc_subnetwork_id)

        self.formFields = [self.txtInputNetwork, self.txtOutputFolder, self.txtResults]
        self.btnReset.clicked.connect(self.reset_form)

        #self.btnExportToTxt.clicked.connect(self.export_to_txt(self.str_results)) # may need to add input parameter for function
        #self.btnDisplayResults.clicked.connect(self.display_results_lyr()) # may need to add input parameter for function
        self.btnClose.clicked.connect(self.close)


    def file_browser(self, txtControl):
        """
        Set QT QLineEdit control to user-specified file name.
        :param txtControl: name of the QLineEdit control
        """
        file_name = QtGui.QFileDialog.getOpenFileName(self, "Open File")
        txtControl.setText(file_name)


    def folder_browser(self, txtControl):
        """
        Set QT QLineEdit control to user-specified folder name.
        :param txtControl: name of the QLineEdit control
        """
        folder_name = QtGui.QFileDialog.getExistingDirectory(self, "Select Folder")
        txtControl.setText(folder_name)


    def reset_form(self):
        for field in self.formFields:
            field.clear()


    def display_log_txt(self, str_results):
        """
        Display results of processing to QT QTextEdit control for display.
        :param txtControl:
        """
        logResults = self.txtResults()
        logResults.moveCursor(QtGui.QTextCursor.End)
        logResults.setValue(str_results)


    def display_results_lyr(self):
        """
        Display processed network shapefile, with a random
        :return:
        """
        pass


    def export_to_txt(self, str_results):
        """
        Exports processing results to a text file.
        :return:
        """
        file_name = QtGui.QFileDialog.getSaveFileName(self,
                                                      'Save Results as Text File',
                                                      '',
                                                      selectedFilter='*.txt')
        with open(file_name, 'w') as file_export:
            file_export.write(str(self.txtResults.toPlainText()))


    def calc_subnetwork_id(self):
        """
        Main processing method, which imports a stream network shapefile,
        converts it to a networkx graph, finds sub-graphs, generates a unique
        identifier for each sub-graph, then converts the graph back to a
        shapefile with a new NetworkID attribute.
        :return:
        """
        start_string = time.ctime()
        start_time = time.time()
        self.display_log_txt("Processing started: {0}".format(start_string))

        self.display_log_txt("Importing stream network shapefile...")
        DG = network.import_shp(self.txtInputNetwork.text())

        self.display_log_txt("Finding subnetworks...")
        list_SG = network.get_subgraphs(DG)

        self.display_log_txt("Calculating subnetwork IDs...")
        UG = network.calc_network_id(list_SG)

        self.display_log_txt("Writing to shapefile...")
        network.export_shp(UG, self.txtOutputFolder.text())

        stop_string = time.ctime()
        stop_time = time.time()
        total_time = round(((stop_time - start_time)/60), 2)
        self.display_log_txt("Processing completed: {0} ".format(stop_string))
        self.display_log_txt("Total processing time: {0} minutes".format(total_time))

        # Display results as text and layers in QGIS TOC
        self.str_results = network.get_graph_attributes(UG, "NetworkID")
        self.display_log_txt(self.str_results)
        # TODO self.display_results_lyr