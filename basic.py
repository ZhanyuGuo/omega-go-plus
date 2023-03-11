#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/22 16:23
# @Author  : Zhanyu Guo
# @Email   : 942568052@qq.com
# @File    : basic.py
# @Software: PyCharm
"""

    MIT License

    Copyright (c) 2021 Zhanyu Guo

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

"""
import sys
import socket
from functools import partial
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen, QBrush
from UI import Dialog, MainWindow

# Chessboard window draws various parameters
# 棋盘窗口绘制的各种参数
SIZE = 30
LINES = 15
OUTER_WIDTH = 20 + 16 * (19 - LINES)  # To fit rows 19 and 15.  为了适配19和15行列
INSIDE_WIDTH = 4
BORDER_WIDTH = 4
LINE_WIDTH = 1
BORDER_LENGTH = SIZE * (LINES - 1) + INSIDE_WIDTH * 2 + BORDER_WIDTH
START_X = START_Y = OUTER_WIDTH + BORDER_WIDTH // 2 + INSIDE_WIDTH
SCREEN_HEIGHT = SIZE * (LINES - 1) + OUTER_WIDTH * 2 + BORDER_WIDTH + INSIDE_WIDTH * 2
SCREEN_WIDTH = SCREEN_HEIGHT + 200

# Size of stones to draw
# 棋子绘制的尺寸
STONE_R1 = SIZE // 2 - 3
STONE_R2 = SIZE // 2 + 3

# Colors
# 颜色
BOARD_COLOR = QColor(0xFA, 0xBE, 0x6E)
BLACK_COLOR = QColor(0, 0, 0)
WHITE_COLOR = QColor(255, 255, 255)
RED_COLOR = QColor(200, 30, 30)
BLUE_COLOR = QColor(30, 30, 200)
BLACK_STONE_COLOR = QColor(45, 45, 45)
WHITE_STONE_COLOR = QColor(219, 219, 219)
YELLOW_STONE_COLOR = QColor(255, 215, 0)

# Offset, which is used to traverse the board.
# 偏移量，用以遍历棋盘
offset = [(1, 0), (0, 1), (1, 1), (1, -1)]


class Chessman:
    """
    Define a Chessman's Properties.
    """

    def __init__(self, name, value, color):
        """
        Init a Chessman.

        :param name: Chessman's name -> str()
        :param value: Chessman's value -> int()
        :param color: Chessman's color -> QColor()
        """
        self.name = name
        self.value = value
        self.color = color


# Three roles
# 三种角色
BLACK_CHESSMAN = Chessman("black", 1, BLACK_STONE_COLOR)
WHITE_CHESSMAN = Chessman("white", 2, WHITE_STONE_COLOR)
YELLOW_CHESSMAN = Chessman("yellow", 3, YELLOW_STONE_COLOR)


class Point:
    """
    Point(x, y) means a point on the board's frame.
    """

    def __init__(self, x=0, y=0):
        """
        Y is from Up to Down, X is from Left to Right.

        :param x: axis x value -> int()
        :param y: axis y value -> int()
        """
        self.x = x
        self.y = y


class Board:
    """
    Define a basic board.
    """

    def __init__(self, lines):
        """
        Init a board.

        :param lines: The dimension of the board.
        """
        self._lines = lines

        # Matrix [LINESxLINES], used to represent the checkerboard
        # 矩阵[LINESxLINES]，用来表示棋盘
        self._board = [[0] * self._lines for _ in range(self._lines)]

        # Current chess player (CHESSMAN).
        # 当前下棋者 (CHESSMAN)
        self.runner = BLACK_CHESSMAN

        # Winner, None means no winner (CHESSMAN).
        # 胜利者，没有则为空 (CHESSMAN)
        self.winner = None

        # History of steps ([Point(), Point(), ...]).
        # 下子记录 ([Point(), Point(), ...])
        self.history = []

        # Number of players (int).
        # 玩家数目（int）
        self.player_num = 2

    def getBoard(self):
        """
        Get current board.

        :return: list()
        """
        return self._board

    def setBoard(self, new_board):
        """
        Set current board

        :param new_board: a new board to set -> list()
        :return: None
        """
        self._board = new_board

    def canDrop(self, point):
        """
        Determine if can drop at the specified point.

        :param point: a specified point -> Point()
        :return: bool()
        """
        return self._board[point.y][point.x] == 0

    def drop(self, chessman, point):
        """
        Drop a stone.

        :param chessman: who -> Chessman()
        :param point: point to drop -> Point()
        :return: the winner (if exists) -> Chessman()
        """
        self._board[point.y][point.x] = chessman.value
        self.history.append(point)

        # Determine victory.
        # 判断胜利
        if self.win(point):
            print(f"{chessman.name} win!")
            return chessman

    def win(self, point):
        """
        Determine if wins

        :param point: point to drop -> Point()
        :return: bool()
        """
        value = self._board[point.y][point.x]
        for item in offset:
            if self.getCountOnDirection(point, value, item[0], item[1]) >= 5:
                return True

    def getCountOnDirection(self, point, value, x_offset, y_offset):
        """
        Get the count of successive pieces on one direction.

        :param point: point to drop -> Point()
        :param value: stone's value -> int()
        :param x_offset: direction on x -> int()
        :param y_offset: direction on y -> int()
        :return: count -> int()
        """
        count = 1
        for step in range(1, 5):
            x = point.x + step * x_offset
            y = point.y + step * y_offset
            if (
                0 <= x < self._lines
                and 0 <= y < self._lines
                and self._board[y][x] == value
            ):
                count += 1
            else:
                break

        for step in range(1, 5):
            x = point.x - step * x_offset
            y = point.y - step * y_offset
            if (
                0 <= x < self._lines
                and 0 <= y < self._lines
                and self._board[y][x] == value
            ):
                count += 1
            else:
                break

        return count

    def getNextRunner(self, runner):
        """
        Get next runner.

        :param runner: current runner -> Chessman()
        :return: next runner -> Chessman()
        """
        if self.player_num == 2:
            if runner == BLACK_CHESSMAN:
                return WHITE_CHESSMAN
            else:
                return BLACK_CHESSMAN

        elif self.player_num == 3:
            if runner == BLACK_CHESSMAN:
                return WHITE_CHESSMAN
            elif runner == WHITE_CHESSMAN:
                return YELLOW_CHESSMAN
            elif runner == YELLOW_CHESSMAN:
                return BLACK_CHESSMAN


class BoardGUI(QMainWindow):
    """
    Board's GUI.
    """

    def __init__(self, lines):
        """
        Generate and Update a GUI, Connected with Server and Update timely.

        :param lines: The dimension of the board.
        """
        super(BoardGUI, self).__init__()

        # Main window
        # 主界面
        self.MainWindowUI = MainWindow.Ui_MainWindow()
        self.MainWindowUI.setupUi(self)
        palette1 = QPalette()  # 颜色，用以配置棋盘背景颜色
        palette1.setColor(self.backgroundRole(), BOARD_COLOR)
        self.setPalette(palette1)

        # Dialog
        # 对话框，提示结束信息
        self.Dialog = QDialog()
        self.DialogUI = Dialog.Ui_Dialog()
        self.DialogUI.setupUi(self.Dialog)

        self._lines = lines

        # Initializes your own checkerboard.
        # 初始化自己的棋盘
        self.board = Board(lines)

        # The server address and port number (default) can be entered later.
        # 服务器地址与端口号（默认值），后续可以输入
        self.url = "http://127.0.0.1:5000/"

        # self.MainWindowUI.lineEditLocalIP.setText(self.getLocalIP())

        # Button callback function initialization.
        # 按钮的回调函数初始化
        # Connect
        # 连接
        self.MainWindowUI.pushButtonConnect.clicked.connect(
            partial(self.connectBtnFn, self.MainWindowUI)
        )
        # Regret
        # 悔棋
        self.MainWindowUI.pushButtonRegret.clicked.connect(self.regret)

        # Rerun
        # 重启
        self.DialogUI.buttonBox.accepted.connect(self.rerun)
        self.DialogUI.buttonBox.rejected.connect(self.notrerun)

    def rerun(self):
        """
        Callback of Dialog OK button

        :return: None
        """
        # Restart a board
        # 重启一个棋盘
        self.board = Board(self._lines)

    def notrerun(self):
        """
        Callback of Dialog Cancel button

        :return: None
        """
        # 使窗口不再弹出
        self.board.winner = None

    def regret(self):
        """
        Callback of regret button.

        :return: None
        """
        # If there is a move, can regret.
        # 如果有步可以悔棋
        if self.board.history:
            last_step = self.board.history.pop(-1)
            board = self.board.getBoard()
            board[last_step.y][last_step.x] = 0
            self.board.setBoard(board)
            self.board.runner = self.board.getNextRunner(self.board.runner)
            self.update()
        else:
            print("Stack is empty, can not regret!")

    def connectBtnFn(self, ui):
        """
        Callback of MainWindow connect button

        :param ui: current ui -> MainWindow()
        :return: None
        """
        dataIn = ui.lineEditServerIP.text()

        if dataIn != "":
            self.url = f"http://{dataIn}:5000/"
        # else:
        #     self.url = 'http://127.0.0.1:5000/'
        #     pass

        ui.labelConnectInfo.setText(self.url)

    def getLocalIP(self):
        """
        Get local IP.

        :return: ip -> str()
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    # Drawing event
    # 绘制事件
    def paintEvent(self, event):
        """
        Update graphically

        :param event: paint event
        :return: None
        """
        qp = QPainter(self)
        # qp.begin(self)

        # anti-aliasing
        # 抗锯齿
        qp.setRenderHint(QPainter.Antialiasing)

        self.drawBoard(qp)
        self.drawStones(qp)

        if self.board.winner is not None:
            self.DialogUI.label.setText(f"{self.board.winner.name} 胜利，游戏结束，是否重新开始？")
            self.Dialog.show()

        # qp.end()

    def drawBoard(self, qp):
        """
        Draw the board.

        :param qp: handler -> QPainter()
        :return: None
        """
        pen = QPen(BLACK_COLOR, BORDER_WIDTH, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawRect(OUTER_WIDTH, OUTER_WIDTH, BORDER_LENGTH, BORDER_LENGTH)
        self.drawLines(qp)

        if self._lines == 19:
            self.drawBoardPoints(qp)

    def drawLines(self, qp):
        """
        Draw lines.

        :param qp: handler -> QPainter()
        :return: None
        """
        pen = QPen(BLACK_COLOR, LINE_WIDTH, Qt.SolidLine)
        qp.setPen(pen)

        # Rows
        # 行
        for i in range(LINES):
            qp.drawLine(
                START_X,
                START_Y + SIZE * i,
                START_X + SIZE * (LINES - 1),
                START_Y + SIZE * i,
            )

        # Columns
        # 列
        for j in range(LINES):
            qp.drawLine(
                START_X + SIZE * j,
                START_Y,
                START_X + SIZE * j,
                START_Y + SIZE * (LINES - 1),
            )

    def drawBoardPoints(self, qp):
        """
        Draw beautifully :)

        :param qp: handler -> QPainter()
        :return: None
        """
        qp.setBrush(BLACK_COLOR)
        for i in (3, 9, 15):
            for j in (3, 9, 15):
                if i == j == 9:
                    r = 5
                else:
                    r = 3
                qp.drawEllipse(
                    START_X + SIZE * i - r, START_Y + SIZE * j - r, r * 2, r * 2
                )

    def drawStones(self, qp):
        """
        Draw exist stones.

        :param qp: handler -> QPainter()
        :return: None
        """
        color = self.board.runner.color

        # Init QPen
        # 初始化画笔
        pen = QPen(color, LINE_WIDTH, Qt.SolidLine)
        brush = QBrush(color)
        qp.setPen(pen)
        qp.setBrush(brush)

        # A piece used for drawing hints.
        # 画提示用的棋子
        qp.drawEllipse(640, 30, STONE_R2 * 2, STONE_R2 * 2)

        # Draw the box for the last step.
        # 画上一步的方框
        if self.board.history:
            last = self.board.history[-1]
            pen.setColor(RED_COLOR)
            brush = QBrush(Qt.NoBrush)
            qp.setPen(pen)
            qp.setBrush(brush)

            qp.drawRect(
                START_X + SIZE * last.x - STONE_R1,
                START_Y + SIZE * last.y - STONE_R1,
                STONE_R1 * 2,
                STONE_R1 * 2,
            )

        # Walk through each row and column to find the existing pieces and draw them.
        # 每行每列遍历寻找存在的棋子并画出
        for i, row in enumerate(self.board.getBoard()):
            for j, cell in enumerate(row):
                if cell == BLACK_CHESSMAN.value:
                    self.drawStone(qp, Point(j, i), BLACK_CHESSMAN.color)
                elif cell == WHITE_CHESSMAN.value:
                    self.drawStone(qp, Point(j, i), WHITE_CHESSMAN.color)
                elif cell == YELLOW_CHESSMAN.value:
                    self.drawStone(qp, Point(j, i), YELLOW_CHESSMAN.color)

        # The game is over, and the chess history is drawn
        # 游戏结束，绘制下棋历史记录
        if self.board.winner:
            for i, point in enumerate(self.board.history):
                num = i + 1
                if num % 2 == 0:
                    pen = QPen(BLACK_STONE_COLOR, LINE_WIDTH, Qt.SolidLine)
                else:
                    pen = QPen(WHITE_STONE_COLOR, LINE_WIDTH, Qt.SolidLine)
                qp.setPen(pen)

                rect = QRectF(
                    START_X + SIZE * point.x - STONE_R1,
                    START_Y + SIZE * point.y - STONE_R1,
                    STONE_R1 * 2,
                    STONE_R1 * 2,
                )
                qp.drawText(rect, Qt.AlignCenter, str(num))

    def drawStone(self, qp, point, stone_color):
        """
        Draw a stone on a specified location.

        :param qp: handler -> QPainter()
        :param point: stone's location on the board -> Point()
        :param stone_color: stone's color -> QColor()
        :return: None
        """
        pen = QPen(stone_color, LINE_WIDTH, Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(stone_color)
        qp.drawEllipse(
            START_X + SIZE * point.x - STONE_R1,
            START_Y + SIZE * point.y - STONE_R1,
            STONE_R1 * 2,
            STONE_R1 * 2,
        )

    # Mouse event
    # 鼠标事件
    def mousePressEvent(self, event):
        """
        Mouse press function.

        :param event: mouse event
        :return: None
        """
        if event.button() == Qt.LeftButton:
            # If there is no winner.
            # 如果没有胜者
            if self.board.winner is None:
                mouse_pos = [event.pos().x(), event.pos().y()]
                # Get the checkerboard position of the mouse
                # 得到鼠标的棋盘位置
                click_point = self.getClickPoint(mouse_pos)

                # It's within the chessboard
                # 在棋盘范围内
                if click_point is not None:
                    if self.board.canDrop(click_point):
                        self.board.winner = self.board.drop(
                            self.board.runner, click_point
                        )
                        self.board.runner = self.board.getNextRunner(self.board.runner)
                else:
                    print("超过棋盘范围...")
                self.update()

    def getClickPoint(self, click_pos):
        """
        Get mouse click point on the board.

        :param click_pos: pixes location -> [int(), int()]
        :return: board axis location (if exists) -> Point()
        """
        pos_x = click_pos[0] - START_X
        pos_y = click_pos[1] - START_Y
        if pos_x < -INSIDE_WIDTH or pos_y < -INSIDE_WIDTH:
            return None
        x = pos_x // SIZE
        y = pos_y // SIZE
        if pos_x % SIZE > SIZE / 2:
            x += 1
        if pos_y % SIZE > SIZE / 2:
            y += 1
        if x >= LINES or y >= LINES:
            return None

        return Point(x, y)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        board_ui = BoardGUI(LINES)

        # Hide something.
        # 隐藏一些暂时用不到的控件
        board_ui.MainWindowUI.widget.hide()
        board_ui.MainWindowUI.labelNowRate.hide()
        board_ui.MainWindowUI.labelHistoryRate.hide()
        board_ui.MainWindowUI.labelWhoAmI.hide()

        board_ui.show()

        sys.exit(app.exec_())
    except Exception as e:
        print(e)
