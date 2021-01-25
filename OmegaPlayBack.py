# -*- coding: utf-8 -*-
# @Time    : 2021/1/4 20:57
# @Author  : Guo_Zhanyu
# @File    : OmegaPlayBack.py
import sqlite3
import time
from BoardBasics import *
import _thread

db = "test.db"
conn = sqlite3.connect(db, check_same_thread=False)
c = conn.cursor()

num = input("输入round:")
last = c.execute("SELECT * from agent where round=%s" % num)


class BoardPB(BoardGUI):
    def __init__(self, lines):
        super(BoardPB, self).__init__(lines)
        self.show()
        pass

    def drawStones(self, qp):
        """
        Draw exist stones.

        :param qp: handler -> QPainter()
        :return: None
        """
        color = self.board.cur_runner.color

        # Init QPen
        # 初始化画笔
        pen = QPen(color, LINE_WIDTH, Qt.SolidLine)
        brush = QBrush(color)
        qp.setPen(pen)
        qp.setBrush(brush)

        # A piece used for drawing hints.
        # 画提示用的棋子
        qp.drawEllipse(650, 30, STONE_R2 * 2, STONE_R2 * 2)

        # Draw the box for the last step.
        # 画上一步的方框
        if self.board.history:
            last = self.board.history[-1]
            pen.setColor(RED_COLOR)
            brush = QBrush(Qt.NoBrush)
            qp.setBrush(brush)
            qp.setPen(pen)
            qp.drawRect(START_X + SIZE * last.x - STONE_R, START_Y + SIZE * last.y - STONE_R,
                        STONE_R * 2, STONE_R * 2)
            pass

        # Walk through each row and column to find the existing pieces and draw them.
        # 每行每列遍历寻找存在的棋子并画出
        for i, row in enumerate(self.board.getBoard()):
            for j, cell in enumerate(row):
                if cell == BLACK_CHESSMAN.value:
                    self.drawStone(qp, Point(j, i), BLACK_CHESSMAN.color)
                elif cell == WHITE_CHESSMAN.value:
                    self.drawStone(qp, Point(j, i), WHITE_CHESSMAN.color)
                    pass
                elif cell == YELLOW_CHESSMAN.value:
                    self.drawStone(qp, Point(j, i), YELLOW_CHESSMAN.color)
                    pass
                pass
            pass

        num = 1
        for point in self.board.history:
            if num % 2 == 0:
                pen = QPen(BLACK_STONE_COLOR, LINE_WIDTH, Qt.SolidLine)
            else:
                pen = QPen(WHITE_STONE_COLOR, LINE_WIDTH, Qt.SolidLine)
                pass
            qp.setPen(pen)
            qp.drawText(START_X + SIZE * point.x - 5, START_Y + SIZE * point.y + 5,
                        str(num))
            num += 1
            pass
        pass
    pass


def threadFn():
    global last

    for row in last:
        time.sleep(0.5)
        value = int(row[0])
        x = int(row[2])
        y = int(row[3])
        board = board_ui.board.getBoard()
        board[y][x] = value
        board_ui.board.setBoard(board)
        board_ui.board.history.append(Point(x, y))
        board_ui.update()
        pass
    pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    board_ui = BoardPB(LINES)
    _thread.start_new_thread(threadFn, ())
    sys.exit(app.exec_())
    pass
