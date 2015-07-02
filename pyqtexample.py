from PyQt4 import QtCore, QtGui

class Window(QtGui.QWidget):
    def __init__(self, path):
        QtGui.QWidget.__init__(self)
        pixmap = QtGui.QPixmap(path)
        layout = QtGui.QGridLayout(self)
        for row in range(4):
            for column in range(4):
                label = QtGui.QLabel(self)
                label.setPixmap(pixmap)
                layout.addWidget(label, row, column)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window(sys.argv[1] if len(sys.argv) else '')
    window.setGeometry(500, 300, 300, 300)
    window.show()
    sys.exit(app.exec_())