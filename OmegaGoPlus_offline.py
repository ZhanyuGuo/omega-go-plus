#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/24 16:41
# @Author  : Zhanyu Guo
# @Email   : 942568052@qq.com
# @File    : OmegaGoPlus_offline.py
# @Software: PyCharm
# from AI.ai_0 import *
# from AI.ai_1 import *
from AI.ai_2 import *
from UI import Choose


class BoardOffline(BoardGUI):
    def __init__(self, lines):
        super(BoardOffline, self).__init__(lines)
        # Who am i
        # 玩家角色
        self.who_am_i = None
        self.ai = None

        # AI class
        # AI 类
        self.ai_class = None

        # 选择颜色的窗口
        self.Choose = QMainWindow()
        self.ChooseUI = Choose.Ui_MainWindow()
        self.ChooseUI.setupUi(self.Choose)
        self.ChooseUI.pushButton.clicked.connect(self.chooseBlack)
        self.ChooseUI.pushButton_2.clicked.connect(self.chooseWhite)
        self.ChooseUI.pushButton_3.hide()
        self.Choose.show()
        pass

    def chooseBlack(self):
        """
        Callback of ChooseUI black button.

        :return: None
        """
        self.who_am_i = BLACK_CHESSMAN
        self.ai = WHITE_CHESSMAN
        self.ai_class = AI(self._lines, self.ai)
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
        self.ai = BLACK_CHESSMAN
        self.ai_class = AI(self._lines, self.ai)
        self.setWindowTitle('Omega White')
        self.show()
        self.Choose.close()

        self.ai_class.setBoard(self.board.getBoard())
        ai_point = self.ai_class.AI_drop()
        self.board.winner = self.board.drop(self.board.runner, ai_point)
        self.board.runner = self.board.getNextRunner(self.board.runner)
        self.update()
        pass

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
                if self.board.runner == self.who_am_i:
                    mouse_pos = [event.pos().x(), event.pos().y()]
                    # Get the checkerboard position of the mouse
                    # 得到鼠标的棋盘位置
                    click_point = self.getClickPoint(mouse_pos)

                    # It's within the chessboard
                    # 在棋盘范围内
                    if click_point is not None:
                        if self.board.canDrop(click_point):
                            self.board.winner = self.board.drop(self.board.runner, click_point)
                            self.board.runner = self.board.getNextRunner(self.board.runner)
                            pass
                        pass
                    else:
                        print('超过棋盘范围...')
                        pass
                    self.update()

                    if self.board.winner is None and self.board.runner == self.ai:
                        self.ai_class.setBoard(self.board.getBoard())
                        ai_point = self.ai_class.AI_drop()

                        self.board.winner = self.board.drop(self.board.runner, ai_point)
                        self.board.runner = self.board.getNextRunner(self.board.runner)
                        self.update()
                        pass
                    pass
                pass
            pass
        pass

    def rerun(self):
        super(BoardOffline, self).rerun()
        if self.who_am_i == WHITE_CHESSMAN:
            self.ai_class.setBoard(self.board.getBoard())
            ai_point = self.ai_class.AI_drop()
            self.board.winner = self.board.drop(self.board.runner, ai_point)
            self.board.runner = self.board.getNextRunner(self.board.runner)
            self.update()
            pass
        pass

    pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = BoardOffline(LINES)
    test.MainWindowUI.widget.hide()
    test.MainWindowUI.labelNowRate.hide()
    test.MainWindowUI.labelHistoryRate.hide()
    test.MainWindowUI.labelWhoAmI.hide()
    sys.exit(app.exec_())
    pass
