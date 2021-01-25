# -*- coding: utf-8 -*-
# from aiGzy0 import *
# from aiGzy1 import *
from aiGzy3 import *
from UI import Choose


class BoardOffline(BoardGUI):
    def __init__(self, lines):
        super(BoardOffline, self).__init__(lines)
        self.who_am_i = None  # Who am i?
        self.ai = None        # AI class

        # 选择颜色的窗口
        self.Choose = QMainWindow()
        self.ChooseUI = Choose.Ui_MainWindow()
        self.ChooseUI.setupUi(self.Choose)
        self.ChooseUI.pushButton.clicked.connect(self.chooseBlack)
        self.ChooseUI.pushButton_2.clicked.connect(self.chooseWhite)
        self.ChooseUI.pushButton_3.hide()
        self.Choose.show()

    def chooseBlack(self):
        """
        Callback of ChooseUI black button.

        :return: None
        """
        self.who_am_i = BLACK_CHESSMAN
        self.ai = AI(self._lines, self.board.getNextRunner(self.who_am_i))
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
        self.ai = AI(self._lines, self.board.getNextRunner(self.who_am_i))
        self.setWindowTitle('Omega White')
        self.show()
        self.Choose.close()

        self.ai.setBoard(self.board.getBoard())
        ai_point = self.ai.AI_drop()
        self.board.winner = self.board.drop(self.board.cur_runner, ai_point)
        self.board.cur_runner = self.board.getNextRunner(self.board.cur_runner)
        self.update()
        pass

    def chooseYellow(self):
        """
        Callback of ChooseUI yellow button.

        :return: None
        """
        # Choose Black for testing AI
        self.who_am_i = BLACK_CHESSMAN
        self.ai = AI(self._lines, self.board.getNextRunner(self.who_am_i))
        self.setWindowTitle('Omega Black')
        self.show()
        self.Choose.close()
        pass

    def mousePressEvent(self, event):
        """
        Mouse press function.

        :param event: mouse event
        :return: None
        """
        if event.button() == Qt.LeftButton:
            # 如果没有胜者
            if self.board.winner is None:
                if self.board.cur_runner == self.who_am_i:
                    mouse_pos = [event.pos().x(), event.pos().y()]
                    # 得到鼠标的棋盘位置
                    click_point = self.getClickPoint(mouse_pos)

                    # 在棋盘范围内
                    if click_point is not None:
                        if self.board.canDrop(click_point):
                            self.board.winner = self.board.drop(self.board.cur_runner, click_point)
                            self.board.cur_runner = self.board.getNextRunner(self.board.cur_runner)
                            pass
                        pass
                    else:
                        print('超过棋盘范围...')
                        pass
                    self.update()

                    if self.board.winner is None and self.board.cur_runner == self.board.getNextRunner(self.who_am_i):
                        self.ai.setBoard(self.board.getBoard())
                        ai_point = self.ai.AI_drop()
                        
                        self.board.winner = self.board.drop(self.board.cur_runner, ai_point)
                        self.board.cur_runner = self.board.getNextRunner(self.board.cur_runner)
                        self.update()
                        pass
                    pass
                pass
            pass
        pass

    def rerun(self):
        super(BoardOffline, self).rerun()
        if self.who_am_i == WHITE_CHESSMAN:
            self.ai.setBoard(self.board.getBoard())
            ai_point = self.ai.AI_drop()
            self.board.winner = self.board.drop(self.board.cur_runner, ai_point)
            self.board.cur_runner = self.board.getNextRunner(self.board.cur_runner)
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
