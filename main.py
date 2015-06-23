import sys
from PyQt4 import QtGui
from random import randint



class Piece(object):

    pieces = ("NE", "NS", "NW", "ES", "EW", "SW", "NSEW")
    def __init__(self):
        pass

    def get_random_piece(self):
        return self.pieces[randint(0,6)]


class Board(object):
    #state[0] is row 1
    #state[1] is row 2
    #state[1][0] is (0, 1)
    pyRows = 10
    pyCols = 7
    realRows = 7
    realCols = 10
    realMaxRow = 6
    realMaxCol = 9
    state = [[x for x in range(0, pyRows)] for j in range(0, pyCols)]
    
    def __init__(self):
        pass

    def set_start_point(self):
        # Return an int 2,3,4,5,6,7,8,9
        x = randint(2, 9)
        # Return an int 2,3,4,5,6
        y = randint(2, 6)
        #   N=0
        # W=3  E=1
        #   S=2
        z = randint(0, 3)
        #self.state[0][1] = 'A'
        self.state[y-1][x-1] = self.int_to_direction(z)

    def int_to_direction(self, number):
        direction = "Z"
        if number == 0:
            direction = 'N'
        elif number == 1:
            direction = 'E'
        elif number == 2:
            direction = 'S'
        elif number == 3:
            direction = 'W'
        return direction

    def print_board(self):
        for row in self.state:
            print row

    def update_board(self, x, y, piece):
        """
        Accept two coordinates (x, y) on the board.
        Update (x, y) to be piece on the board."""
        self.state[y][x] = piece

class PipeView(QtGui.QWidget):

    layout = None
    def __init__(self):
        super(PipeView, self).__init__()
        self.init_ui()
        self.draw_tiles()

    def init_ui(self):
        self.layout = QtGui.QGridLayout(self)
        self.layout.setSpacing(1)
        self.setLayout(self.layout)
        self.setGeometry(500, 300, 800, 600)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('intersection.jpg'))
        lbl1 = QtGui.QLabel('a i d s', self)
        lbl1.move(15, 10)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def draw_tiles(self):
        pixmap = QtGui.QPixmap('intersection.jpg')
        for row in range(7):
            for column in range(10):
                label = QtGui.QLabel(self)
                label.setPixmap(pixmap)
                label.setScaledContents(True)
                self.layout.addWidget(label, row, column)


class PipeModel(PipeView):

    def __init__(self):
        pass





class PipeController(PipeModel, PipeView):

    def __init__(self):
        pass




class PipeDream(object):

    def __init__(self):
        b = Board()
        b.set_start_point()
        b.update_board(0, 1, "A")
        b.print_board()
        p = Piece()
        print p.get_random_piece()




def main():
    app = QtGui.QApplication(sys.argv)
    view = PipeView()
    application = PipeDream()
    # w = QtGui.QWidget()
    #w.resize(800, 600)
    #w.move(100, 100)
    #w.setWindowTitle('Simple')
    #w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()