import sys
import PyQt4.QtGui as QtGui
from PyQt4.QtCore import *
from random import randint
import eQLabel
ROWS = 10
COLS = 10

class Tile(QtGui.QLabel):
    pos = []
    def set_pos(self, pos):
        self.pos = pos
    def mouseReleaseEvent(self, event):
        print (self.pos)

class Piece(object):
    pieces = ("NE", "NS", "NW", "ES", "EW", "SW", "NSEW")
    def __init__(self):
        pass
    def get_random_piece(self):
        #TODO: weight items
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
    start = []
    
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
        self.start = [x-1, y-1, z]

    def get_start_point(self):
        return self.start

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
            print (row)

    def update_board(self, x, y, piece):
        """
        Accept two coordinates (x, y) on the board.
        Update (x, y) to be piece on the board."""
        self.state[y][x] = piece

class PipeView(QtGui.QWidget):

    layout = None
    lbl_score = None
    lbl_level = None
    info_font = None
    tiles = None

    def __init__(self):
        super(PipeView, self).__init__()
        self.info_font = QtGui.QFont("Georgia", 12, 12, False)
        self.tiles = [[x for x in range(0, ROWS)] for j in range(0, COLS)]
        self.init_ui()


    def init_ui(self):
        self.layout = QtGui.QGridLayout(self)
        self.layout.setSpacing(1)
        self.setLayout(self.layout)
        self.setGeometry(500, 300, 800, 600)
        self.setWindowTitle('Pipe Dream - by Henry Chladil')
        self.setWindowIcon(QtGui.QIcon('assets/intersection.jpg'))
        self.center_window()
        self.draw_tiles()
        self.draw_next_tiles()
        self.draw_info()
        self.show()

    def center_window(self):
        frame_geo = self.frameGeometry()
        center_point = QtGui.QDesktopWidget().availableGeometry().center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())

    def draw_info(self):
        self.lbl_score = QtGui.QLabel(self)
        self.lbl_score.setText("Score: 0")
        self.lbl_score.setScaledContents(True)
        self.lbl_score.setFont(self.info_font)
        self.layout.addWidget(self.lbl_score, 0, 0)

        self.lbl_level = QtGui.QLabel(self)
        self.lbl_level.setScaledContents(True)
        self.lbl_level.setText("Level: 1")
        self.layout.addWidget(self.lbl_level, 0, 1)
        self.lbl_level.setFont(self.info_font)

    def draw_next_tiles(self):
        pixmap = QtGui.QPixmap('assets/intersection.jpg')
        for column in range(5, 10):
            label = QtGui.QLabel(self)
            label.setPixmap(pixmap)
            label.setScaledContents(True)
            self.layout.addWidget(label, 0, column)

    def draw_tiles(self):
        pixmap = QtGui.QPixmap('assets/intersection.jpg')
        for row in range(1, COLS+1):
            for column in range(ROWS):
                label = Tile(self)
                label.set_pos([row - 1, column])
                label.setScaledContents(True)
                label.setObjectName("Label%d:%d" % (row - 1, column))
                #label.setText("%d:%d" % (row - 1, column))
                label.setPixmap(pixmap)
                #label.mousePressEvent(self.button_released)
                #label.mousePressEvent = self.handle_click
                self.layout.addWidget(label, row, column)
                self.tiles[row-1][column-1] = label
    def handle_click(self, event):
        print (event.globalX())
        print (event.globalY())
        print (event.x())
        print (event.y())
        print (event.pos())
        print (event.button())
        #print (self.tiles)

        for row in self.tiles:
            print (row)
        for row in self.tiles:
            for col in row:
                if col == event:
                    print ("found :)")
        #print (self.tiles[event])
        print ("")

    def button_released(self):
        sending_button = self.sender()
        self.status_label.setText('%s Clicked!' % str(sending_button.objectName()))

    def set_level(self, level):
        self.lbl_level.setText("Level: " + str(level))
        self.show()

    def set_score(self, score):
        self.lbl_score.setText("Score: " + str(score))
        self.show()


class PipeModel(object):

    level = 0
    score = 0
    view = None

    def __init__(self, view):
        self.init_board()
       
        p = Piece()
        self.view = view
        self.level = 1

    def init_board(self):
        b = Board()
        b.set_start_point()
        start = b.get_start_point()

        #b.update_board(0, 1, "A")
        #b.print_board()

    def set_level(self, level):
        self.level = level
        self.view.set_level(level)

    def get_level(self):
        return self.level

    def set_score(self, score):
        self.score = score
        self.view.set_score(score)

    def get_score(self):
        return score


class PipeController(object):

    def __init__(self, model, view):
        
        pass

class PipeDream(object):

    running = False
    model = None
    view = None
    controller = None

    def __init__(self, model, view, controller):
        self.running = True
        self.run()
        #print p.get_random_piece()
        model.set_level(2)
        model.set_score(10)

    def run(self):
        #while self.running:
            #pass



def main():
    app = QtGui.QApplication(sys.argv)
    view = PipeView()
    model = PipeModel(view)
    controller = PipeController(model, view)
    application = PipeDream(model, view, controller)
    # w = QtGui.QWidget()
    #w.resize(800, 600)
    #w.move(100, 100)
    #w.setWindowTitle('Simple')
    #w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()