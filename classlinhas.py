# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ClassLinhas
                                 A QGIS plugin
 Divide em uma classificação pro comprimentos
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-07-20
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Luiz Zamprogno
        email                : lpzampronio@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5 import QtCore
from PyQt5.QtCore import QVariant

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .classlinhas_dialog import ClassLinhasDialog
import os.path

from qgis.core import QgsMapLayerProxyModel, QgsFieldProxyModel, QgsField, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, edit, QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsSymbol
from PyQt5.QtGui import QColor


class ClassLinhas:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ClassLinhas_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Classificação de comprimentos')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ClassLinhas', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/classlinhas/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Análise de Linhas'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Classificação de comprimentos'),
                action)
            self.iface.removeToolBarIcon(action)

    def closeWindow(self):
        self.dlg.close()

    # função principal
    def execucao(self):
        field = 'classes'
        layer = self.dlg.mcbLinhas.currentLayer()
        indice = layer.fields().indexFromName(field)
        exp = 'case\r\nwhen  \"comp\" <= 200 then \'<200 m\'\r\nwhen  \"comp\" > 200 and \"comp\" <= 300 then \'200 - 300 m\'\r\nwhen  \"comp\" > 300 and \"comp\" <= 400 then \'300 - 400 m\'\r\nwhen  \"comp\" > 400 and \"comp\" <= 500 then \'400 - 500 m\'\r\nwhen  \"comp\" > 500 and \"comp\" <= 600 then \'500 - 600 m\'\r\nwhen  \"comp\" > 600 then \'>600 m\'\r\nend'

        def createField (nomeCampo, tipoCampo, comprimento, precisao):

            provedor = layer.dataProvider()
            provedor.addAttributes([QgsField(nomeCampo, tipoCampo, len=comprimento, prec=precisao)])
            layer.updateFields()

            expressao = QgsExpression(exp)
            contexto = QgsExpressionContext()
            contexto.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))


            with edit (layer):
                for atributo in layer.getFeatures():
                    contexto.setFeature(atributo)
                    atributo[nomeCampo] = expressao.evaluate(contexto)
                    layer.updateFeature(atributo)


        def lineStyles():

            parametros = {'<200 m':('#d7191c', '<200 m'), 
                        '200 - 300 m':('#f69053', '200 - 300 m'), 
                        '300 - 400 m':('#ffdf9a', '300 - 400 m'), 
                        '400 - 500 m':('#def2b4', '400 - 500 m'), 
                        '500 - 600 m':('#91cba9', '500 - 600 m'), 
                        '>600 m':('#2b83ba', '>600 m')}
            categories = []

            for parametro, (color, label) in parametros.items():
                sym = QgsSymbol.defaultSymbol(layer.geometryType())
                sym.setColor(QColor(color))
                category = QgsRendererCategory(parametro, sym, label)
                categories.append(category)

            renderer = QgsCategorizedSymbolRenderer(field, categories)
            layer.setRenderer(renderer)
            layer.triggerRepaint()


        #Executar funções
        if indice == -1:
            createField(field, QVariant.String, 50, 50)
        else:
            print('O campo {}, já existe no layer {}'.format(field, layer.name()))

        lineStyles() 

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = ClassLinhasDialog()

            self.dlg.mcbLinhas.setFilters(QgsMapLayerProxyModel.LineLayer)
            self.dlg.fcbCampo.setFilters(QgsFieldProxyModel.Double)

            self.dlg.fcbCampo.setLayer(self.dlg.mcbLinhas.currentLayer())

            self.dlg.btnOk.clicked.connect(self.execucao)
            self.dlg.btnCancel.clicked.connect(self.closeWindow)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
