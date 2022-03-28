from PySide2.QtWidgets import (QVBoxLayout, QPushButton, QWidget, QSizePolicy)
from PySide2.QtGui import (QIcon)
from PySide2.QtCore import Qt

from ..core.style_handler import icon_path

class CollapseWidget(QWidget):
    def __init__(self, text=str, widget=QWidget, collapse=bool(True), parent=None):
        """
         Collapsable widget
        """
        super(CollapseWidget, self).__init__(parent)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(2)
        mainLayout.setAlignment(Qt.AlignTop)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.rightArrow = QIcon(icon_path('anima-arrow-right-01', 'svg'))
        self.downArrow = QIcon(icon_path('anima-arrow-down-01', 'svg'))

        self.toggle = QPushButton(text)
        self.toggle.setIcon(self.downArrow)
        self.toggle.setLayoutDirection(Qt.LeftToRight)
        self.toggle.setStyleSheet('''QPushButton{
                                    background-color: rgb(83,83,83);
                                    width: 10px;
                                    height: 20px;
                                    font-size: 11px;
                                    border-style: outset;
                                    border-width: 0px;
                                    border-color: rgb(0,0,0);
                                    border-radius: 1px;
                                    text-align: left;
                                    color: rgb(187,187,187);
                                    padding-left: 5px;
                                    }
                                    QPushButton:focus{
                                    border: none;
                                    outline: none;
                                    }''')
        self.toggle.clicked.connect(self.toggleWidget)

        self.widget = widget

        mainLayout.addWidget(self.toggle)
        mainLayout.addWidget(self.widget)
        
        # Default on Off mood
        self.toggle.setIcon(self.rightArrow)
        if collapse:
            self.widget.setVisible(False)
        else:
            self.widget.setVisible(True)

    def toggleWidget(self):
        if self.widget.isVisible():
            self.toggle.setIcon(self.rightArrow)
            self.widget.setVisible(False)
        else:
            self.toggle.setIcon(self.downArrow)
            self.widget.setVisible(True)
 