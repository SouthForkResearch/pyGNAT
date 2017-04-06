# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GNAT
                                 A QGIS plugin
 Build and analyze geomorphic attributes of stream networks
                             -------------------
        begin                : 2017-04-05
        copyright            : (C) 2017 by South Fork Research, Inc.
        email                : jesse@southforkresearch.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GNAT class from file GNAT.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .build_network import GNAT
    return GNAT(iface)
