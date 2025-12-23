# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'review_browser.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
AYON = False
try:
    from qtpy.QtCore import *
    from qtpy.QtGui import *
    from qtpy.QtWidgets import *
    from ayon_core import style
    AYON = True
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


class Ui_BrowserWidget(object):
    def setupUi(self, BrowserWidget):
        if not BrowserWidget.objectName():
            BrowserWidget.setObjectName(u"BrowserWidget")
        BrowserWidget.resize(699, 626)
        if AYON:
            BrowserWidget.setStyleSheet(style.load_stylesheet())

        self.centralwidget = QWidget(BrowserWidget)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_main = QVBoxLayout(self.centralwidget)
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        self.filtersLayout = QHBoxLayout()
        self.filtersLayout.setObjectName(u"filtersLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.filtersLayout.addItem(self.horizontalSpacer)

        self.toolButton = QToolButton(self.centralwidget)
        self.toolButton.setObjectName(u"toolButton")

        self.filtersLayout.addWidget(self.toolButton)


        self.verticalLayout_main.addLayout(self.filtersLayout)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabReviewSubmission = QWidget()
        self.tabReviewSubmission.setObjectName(u"tabReviewSubmission")
        self.reviewSubmissionLayout = QHBoxLayout(self.tabReviewSubmission)
        self.reviewSubmissionLayout.setObjectName(u"reviewSubmissionLayout")
        self.tableView_review_versions = QTableView(self.tabReviewSubmission)
        self.tableView_review_versions.setObjectName(u"tableView_review_versions")

        self.reviewSubmissionLayout.addWidget(self.tableView_review_versions)

        self.tabWidget.addTab(self.tabReviewSubmission, "")
        self.tabLists = QWidget()
        self.tabLists.setObjectName(u"tabLists")
        self.listsLayout = QHBoxLayout(self.tabLists)
        self.listsLayout.setObjectName(u"listsLayout")
        self.splitterLists = QSplitter(self.tabLists)
        self.splitterLists.setObjectName(u"splitterLists")
        self.splitterLists.setOrientation(Qt.Orientation.Horizontal)

        self.leftWidget = QWidget(self.splitterLists)
        self.leftWidget.setObjectName(u"leftWidget")
        self.leftLayout = QVBoxLayout(self.leftWidget)
        self.leftLayout.setObjectName(u"leftLayout")

        self.searchLineEdit = QLineEdit(self.leftWidget)
        self.searchLineEdit.setObjectName(u"searchLineEdit")
        self.searchLineEdit.setPlaceholderText(QCoreApplication.translate("BrowserWidget", u"Search lists...", None))
        self.leftLayout.addWidget(self.searchLineEdit)

        self.listView = QListView(self.leftWidget)
        self.listView.setObjectName(u"listView")
        self.leftLayout.addWidget(self.listView)

        self.splitterLists.addWidget(self.leftWidget)

        self.tableView_list_versions = QTableView(self.splitterLists)
        self.tableView_list_versions.setObjectName(u"tableView_list_versions")
        self.splitterLists.addWidget(self.tableView_list_versions)

        self.listsLayout.addWidget(self.splitterLists)

        self.tabWidget.addTab(self.tabLists, "")

        self.verticalLayout_main.addWidget(self.tabWidget)

        BrowserWidget.setCentralWidget(self.centralwidget)

        self.retranslateUi(BrowserWidget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(BrowserWidget)
    # setupUi

    def retranslateUi(self, BrowserWidget):
        BrowserWidget.setWindowTitle(QCoreApplication.translate("BrowserWidget", u"Review Browser", None))
        self.toolButton.setText(QCoreApplication.translate("BrowserWidget", u"...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabReviewSubmission), QCoreApplication.translate("BrowserWidget", u"Review Submission", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabLists), QCoreApplication.translate("BrowserWidget", u"Lists", None))
    # retranslateUi
