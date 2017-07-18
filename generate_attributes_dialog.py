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
import network as network
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
        # assign edge types
        # assign node types
        # calculate river kilometers from mouth
        # calculate stream order
        # assign branch ID
        # display output by edge type (?)
