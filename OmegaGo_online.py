# -*- coding: utf-8 -*-
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
from BoardBasics import *
import aiGzy3
import aiGst
import Choose
import Choose0
import requests
import _thread
import time


class BoardClient(BoardGUI):
    """
    Client
    """
    def __init__(self, lines):
        """
        Generate and Update a GUI, Connected with Server and Update timely.

        :param lines: The dimension of the board.
        """
        super(BoardClient, self).__init__(lines)
        self.who_am_i = None  # Who am i?
        self.ai = None        # AI class
        self.id = 0           # Player's id
        self.state = 0        # Game's state (0: init, 1: active, 2: idle, 3:over)
        self.connected = False

        self.players = 1
        self.cur_players = 1

        self.MainWindowUI.pushButtonRestart.hide()

        self.Choose0 = QMainWindow()
        self.Choose0UI = Choose0.Ui_MainWindow()
        self.Choose0UI.setupUi(self.Choose0)
        self.Choose0UI.pushButton2.clicked.connect(self.choose2)
        self.Choose0UI.pushButton3.clicked.connect(self.choose3)
        self.Choose0.show()

        # Window of selecting the color.
        # 选择颜色的窗口
        self.Choose = QMainWindow()
        self.ChooseUI = Choose.Ui_MainWindow()
        self.ChooseUI.setupUi(self.Choose)
        self.ChooseUI.pushButton.clicked.connect(self.chooseBlack)
        self.ChooseUI.pushButton_2.clicked.connect(self.chooseWhite)
        self.ChooseUI.pushButton_3.clicked.connect(self.chooseYellow)

        # Player or AI mode
        # 玩家 or AI模式
        self.mode = 0
        self.MainWindowUI.pushButtonSetPlayer.clicked.connect(self.setPlayerMode)
        self.MainWindowUI.pushButtonSetAI.clicked.connect(self.setAIMode)

        self.notre = False
        self.MainWindowUI.pushButtonRestart.clicked.connect(self.restart)

        self.history_rate = None
        self.now_rate = None
        self.MainWindowUI.pushButtonRegret.hide()
        pass

    def restart(self):
        if self.state in [2, 3]:
            self.postRestBoard(-1, -1)
            self.MainWindowUI.pushButtonRestart.hide()
            pass
        pass

    def choose2(self):
        self.players = 2
        self.Choose0.close()
        self.Choose.show()
        self.ChooseUI.pushButton_3.hide()
        pass

    def choose3(self):
        self.players = 3
        self.Choose0.close()
        self.Choose.show()
        pass

    def chooseBlack(self):
        """
        Callback of ChooseUI black button.

        :return: None
        """
        self.who_am_i = BLACK_CHESSMAN
        if self.players == 2:
            self.ai = aiGzy3.AI(self._lines, self.who_am_i)
        elif self.players == 3:
            self.ai = aiGst.AI(self._lines, self.who_am_i)
            pass

        self.setWindowTitle('Omega Black')
        self.show()
        self.Choose.close()
        pass

    def chooseWhite(self):
        """
        Callback of ChooseUI white button.

        :return: None
        """
        self.who_am_i = WHITE_CHESSMAN
        if self.players == 2:
            self.ai = aiGzy3.AI(self._lines, self.who_am_i)
        elif self.players == 3:
            self.ai = aiGst.AI(self._lines, self.who_am_i)
            pass

        self.setWindowTitle('Omega White')
        self.show()
        self.Choose.close()
        pass

    def chooseYellow(self):
        """
        Callback of ChooseUI yellow button.

        :return: None
        """
        self.who_am_i = YELLOW_CHESSMAN
        self.ai = aiGst.AI(self._lines, self.who_am_i)

        self.setWindowTitle('Omega Yellow')
        self.show()
        self.Choose.close()
        pass

    def setPlayerMode(self):
        """
        Callback of player mode.

        :return: None
        """
        self.mode = 0
        self.MainWindowUI.labelMode.setText("当前模式：玩家模式")
        pass

    def setAIMode(self):
        """
        Callback of AI mode.

        :return: None
        """
        if self.cur_players in [2, 3]:
            self.mode = 1
            self.MainWindowUI.labelMode.setText("当前模式：AI模式")
        pass

    def regret(self):
        """
        Callback of regret button.

        :return: None
        """
        # 如果有步可以悔棋
        # if self.board.history:
        #     board = self.board.getBoard()
        #     board[self.board.last.y][self.board.last.x] = 0
        #     self.board.setBoard(board)
        #     self.board.cur_runner = self.board.getNextRunner(self.board.cur_runner)
        #
        #     self.board.history.pop(-1)
        #     if self.board.history:
        #         self.board.last = self.board.history[-1]
        #     else:
        #         self.board.last = None
        #
        #     requests.get(self.url + 'rest/regret')
        #     self.update()
        # else:
        #     print('Can not regret')
        #     pass

        pass

    def mousePressEvent(self, event):
        """
        Mouse press function.

        :param event: mouse event
        :return: None
        """
        if event.button() == Qt.LeftButton:
            if self.connected and self.cur_players in [2, 3] and self.state not in [2, 3] and self.board.cur_runner.name == self.who_am_i.name and self.mode == 0:
                # If there is no winner, current round, player mode.
                # 如果没有胜者、当前轮次、玩家模式
                mouse_pos = [event.pos().x(), event.pos().y()]

                # Get the checkerboard position of the mouse.
                # 得到鼠标的棋盘位置
                click_point = self.getClickPoint(mouse_pos)

                # It's within the chessboard
                # 在棋盘范围内
                if click_point is not None:
                    if self.board.canDrop(click_point):
                        self.board.drop(self.board.cur_runner, click_point)
                        self.postRestBoard(click_point.x, click_point.y)
                        pass
                    pass
                else:
                    print('超过棋盘范围...')
                    pass
                self.update()
                pass
            pass
        pass

    def paintEvent(self, event):
        """
        Update graphically

        :param event: paint event
        :return: None
        """
        qp = QPainter(self)
        qp.begin(self)

        # anti-aliasing
        # 抗锯齿
        qp.setRenderHint(QPainter.Antialiasing)
        self.drawBoard(qp)   # Draw board.  画棋盘
        self.drawStones(qp)  # Draw stones. 画棋子
        self.drawWho(qp)     # Draw who.    画出自己的颜色

        # Game over.
        if self.state == 3 and not self.notre:
            self.Dialog.show()
            self.MainWindowUI.pushButtonRestart.show()
            pass

        if self.history_rate is not None:
            self.MainWindowUI.labelHistoryRate.setText("历史胜率：%.2f%%" % self.history_rate)
            pass
        if self.now_rate is not None:
            self.MainWindowUI.labelNowRate.setText("实时胜率：%.2f%%" % self.now_rate)
            pass

        qp.end()
        pass

    def drawWho(self, qp):
        color = self.who_am_i.color
        pen = QPen(color, LINE_WIDTH, Qt.SolidLine)
        brush = QBrush(color)
        qp.setPen(pen)
        qp.setBrush(brush)

        qp.drawEllipse(740, 30, STONE_R2*2, STONE_R2*2)
        pass

    def rerun(self):
        """
        Callback of Dialog OK button

        :return: None
        """
        # Submit a reset board request.
        # 提交重置棋盘申请
        self.postRestBoard(-1, -1)

        # Update game status.
        # 更新游戏状态
        self.getRestPlay()  # state <- new_state
        self.getRestActionLast()

        pass

    def notrerun(self):
        """
        Callback of Dialog Cancel button

        :return: None
        """
        self.notre = True
        # # 没想好不继续要进行什么处理，暂且重开同样操作
        # self.postRestBoard(-1, -1)
        # # 更新游戏状态
        # self.getRestPlay()  # state <- new_state
        pass

    def closeEvent(self, event):
        """
        Click on X (exit) callback.

        :param event:
        :return: None
        """
        # Submit a reset board request.
        # 提交重置棋盘申请
        if self.connected:
            self.postRestBoard(-2, -2)
            pass
        pass

    def connectBtnFn(self, ui):
        """
        Callback of MainWindow connect button

        :param ui: current ui -> MainWindow()
        :return: None
        """
        if not self.connected:
            dataIn = ui.lineEditServerIP.text()
            if dataIn != '':
                self.url = f'http://{dataIn}:5000/'
                pass
            ui.labelConnectInfo.setText(self.url)
            self.postRestPlayer()
            self.getRestPlayer()

            # Start a thread.
            # 开启线程
            _thread.start_new_thread(self.operate_thread, ())
            # _thread.start_new_thread(self.update_thread, ())
            self.connected = True
            pass
        pass

    def update_thread(self):
        while True:
            time.sleep(0.1)
            self.update()
            pass
        pass

    def operate_thread(self):
        """
        Timer.

        :return: None
        """
        while True:
            time.sleep(0.5)
            try:
                self.getRestPlayReport()
                # Update the board
                # 更新棋盘
                self.getRestBoard()  # board <- new_board

                # Update the information
                # 更新信息
                self.getRestPlayer()  # id, board.players

                # Update current cycle/last step
                # 更新当前轮次/最后一步
                self.getRestActionLast()  # current_runner, last <- new*

                # Update game state
                # 更新游戏状态
                self.getRestPlay()  # state <- new_state

                # self.update()
                if self.state not in [2, 3]:
                    self.notre = False
                    pass

                # AI drop
                # AI下子
                if self.cur_players in [2, 3] and self.mode == 1 and self.board.cur_runner.name == self.who_am_i.name and self.state not in [2, 3]:
                    AI_point = self.ai.AI_drop()
                    self.board.drop(self.who_am_i, AI_point)
                    self.board.cur_runner = self.board.getNextRunner(self.board.cur_runner)

                    # Submit
                    # 提交
                    self.postRestBoard(AI_point.x, AI_point.y)
                    pass

                # Update the board
                # 更新棋盘
                self.getRestBoard()     # board <- new_board

                # Update current cycle/last step
                # 更新当前轮次/最后一步
                self.getRestActionLast()  # current_runner, last <- new*

                # Update game state
                # 更新游戏状态
                self.getRestPlay()  # state <- new_state

                self.update()
            except Exception as e:
                self.MainWindowUI.labelConnectInfo.setText('连接失败...')
                print(e)
                pass
            pass
        pass

    def getRestPlay(self):
        """
        Get game's state.

        :return: None
        """
        r = requests.get(self.url + 'rest/play')
        rev = r.json()
        # print(rev, type(rev))
        self.state = rev
        pass

    def postRestPlayer(self):
        """
        postRestPlayer

        :return: None
        """
        try:
            post = dict()
            post['ip'] = self.getLocalIP()
            post['color'] = self.who_am_i.name
            r1 = requests.post(self.url + 'rest/player', data=post)
            rev = r1.json()
            # print(rev, type(rev))
        except Exception as ee:
            self.MainWindowUI.label_3.setText('连接失败...')
            print(ee)
        pass

    def getRestPlayer(self):
        """
        Get id.

        :return: None
        """
        r = requests.get(self.url + 'rest/player')
        rev = r.json()
        # print(rev, type(rev))
        self.id = rev[self.who_am_i.name]
        self.cur_players = len(rev.keys())
        pass

    def getRestBoard(self):
        """
        Get Board from server.

        :return: None
        """
        r = requests.get(self.url + 'rest/board')
        rev = r.json()
        # print(rev, type(rev))
        new_board = rev['board']
        self.board.setBoard(new_board)
        self.ai.setBoard(new_board)
        pass

    def getRestActionLast(self):
        """
        Get last info.

        :return: None
        """
        r = requests.get(self.url + 'rest/action/last')
        rev = r.json()
        # print(rev, type(rev))
        # error
        if isinstance(rev, str):
            self.board.cur_runner = BLACK_CHESSMAN
            self.board.history = []
        else:
            if self.cur_players != 1:
                self.board.cur_runner = self.getCurrent(rev['playerid'])
                pass

            self.board.last = Point(rev['x'], rev['y'])
            if not self.board.history:
                self.board.history.append(self.board.last)
                pass

            if self.board.last != self.board.history[-1]:
                self.board.history.append(self.board.last)
                pass

            pass
        pass

    def getCurrent(self, id_):
        if self.cur_players == 2:
            if id_ == 1:
                return WHITE_CHESSMAN
            else:
                return BLACK_CHESSMAN
        elif self.cur_players == 3:
            if id_ == 1:
                return WHITE_CHESSMAN
            elif id_ == 2:
                return YELLOW_CHESSMAN
            else:
                return BLACK_CHESSMAN
            pass
        pass

    def postRestBoard(self, x, y):
        """
        Post Board.

        :param x: new x -> int()
        :param y: new y -> int()
        :return: None
        """
        send = dict()
        send['id'] = self.id
        send['x'] = x
        send['y'] = y
        send['color'] = self.who_am_i.name
        r = requests.post(self.url + 'rest/board', data=send)
        # rev = r.json()
        # print(rev, type(rev))
        pass

    def getRestPlayReport(self):
        r = requests.get(self.url + 'rest/play/report')
        rev = r.json()
        # print(rev)
        if self.players == 2:
            if sum(rev[0:2]):
                self.history_rate = rev[self.who_am_i.value - 1] / sum(rev[0:2]) * 100
                pass

            if self.who_am_i == BLACK_CHESSMAN:
                self.now_rate = rev[2]
            elif self.who_am_i == WHITE_CHESSMAN:
                self.now_rate = 100 - rev[2]
                pass
            pass
        elif self.players == 3:
            if sum(rev[0:3]):
                self.history_rate = rev[self.who_am_i.value - 1] / sum(rev[0:3])*100
                pass

            if self.who_am_i == BLACK_CHESSMAN:
                self.now_rate = rev[3]
            elif self.who_am_i == WHITE_CHESSMAN:
                self.now_rate = rev[4]
            else:
                self.now_rate = 100 - (rev[3] + rev[4])
                pass
            pass
        pass

    pass


def main():
    client = QApplication(sys.argv)
    board_client = BoardClient(LINES)
    sys.exit(client.exec_())
    pass


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        pass
    pass
