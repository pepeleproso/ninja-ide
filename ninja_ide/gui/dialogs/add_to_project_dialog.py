# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import

import os

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.tools.ui_tools import ThreadExecution, LoadingItem
from ninja_ide.core.file_handling import file_manager

###############################################################################
# ADD TO PROJECT
###############################################################################


class AddToProject(QDialog):

    def __init__(self, pathProjects, parent=None):
        #pathProjects must be a list
        QDialog.__init__(self, parent)
        self.setWindowTitle(self.tr("Add File to Project"))
        self.pathSelected = ''
        vbox = QVBoxLayout(self)

        self._tree = QTreeWidget()
        self._tree.header().setHidden(True)
        self._tree.setSelectionMode(QTreeWidget.SingleSelection)
        self._tree.setAnimated(True)
        vbox.addWidget(self._tree)
        hbox = QHBoxLayout()
        btnAdd = QPushButton(self.tr("Add here!"))
        btnCancel = QPushButton(self.tr("Cancel"))
        hbox.addWidget(btnCancel)
        hbox.addWidget(btnAdd)
        vbox.addLayout(hbox)
        #load folders
        self._root = None
        self._loading_items = {}
        self.loading_projects(pathProjects)
        self._thread_execution = ThreadExecution(
            self._thread_load_projects, args=[pathProjects])
        self.connect(self._thread_execution,
            SIGNAL("finished()"), self._callback_load_project)
        self._thread_execution.start()

        self.connect(btnCancel, SIGNAL("clicked()"), self.close)
        self.connect(btnAdd, SIGNAL("clicked()"), self._select_path)

    def loading_projects(self, projects):
        for project in projects:
            loadingItem = LoadingItem()
            item = loadingItem.add_item_to_tree(project, self._tree,
                parent=self)
            self._loading_items[project] = item

    def _thread_load_projects(self, projects):
        structures = []
        for pathProject in projects:
            folderStructure = file_manager.open_project(pathProject)
            structures.append((folderStructure, pathProject))
        self._thread_execution.storage_values = structures

    def _callback_load_project(self):
        structures = self._thread_execution.storage_values
        if structures:
            for structure, path in structures:
                item = self._loading_items.pop(path, None)
                if item is not None:
                    index = self._tree.indexOfTopLevelItem(item)
                    self._tree.takeTopLevelItem(index)
                self._load_project(structure, path)

    def _select_path(self):
        item = self._tree.currentItem()
        if item:
            self.pathSelected = item.toolTip(0)
            self.close()

    def _load_project(self, folderStructure, folder):
        if not folder:
            return

        name = file_manager.get_basename(folder)
        item = QTreeWidgetItem(self._tree)
        item.setText(0, name)
        item.setToolTip(0, folder)
        item.setIcon(0, QIcon(resources.IMAGES['tree-folder']))
        if folderStructure[folder][1] is not None:
            folderStructure[folder][1].sort()
        self._load_folder(folderStructure, folder, item)
        item.setExpanded(True)
        self._root = item

    def _load_folder(self, folderStructure, folder, parentItem):
        items = folderStructure[folder]

        if items[1] is not None:
            items[1].sort()
        for _file in items[1]:
            if _file.startswith('.'):
                continue
            subfolder = QTreeWidgetItem(parentItem)
            subfolder.setText(0, _file)
            subfolder.setToolTip(0, os.path.join(folder, _file))
            subfolder.setIcon(0, QIcon(resources.IMAGES['tree-folder']))
            self._load_folder(folderStructure,
                os.path.join(folder, _file), subfolder)