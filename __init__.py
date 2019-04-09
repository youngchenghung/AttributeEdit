# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AttributeEdit
                                 A QGIS plugin
 edittool
                             -------------------
        begin                : 2018-11-14
        copyright            : (C) 2018 by  
        email                :  
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
    """Load AttributeEdit class from file AttributeEdit.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .attribute_edit import AttributeEdit
    return AttributeEdit(iface)
