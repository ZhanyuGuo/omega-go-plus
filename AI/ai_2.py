#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/25 12:07
# @Author  : Zhanyu Guo
# @Email   : 942568052@qq.com
# @File    : ai_2.py
# @Software: PyCharm
from AI.ChessAI2 import *
from basic import *


class AI(ChessAI):
    def __init__(self, lines, chessman):
        super(AI, self).__init__(lines)
        self.value = chessman.value
        self._board = [[0] * self.len for _ in range(self.len)]
        pass

    def setBoard(self, new_board):
        self._board = new_board
        pass

    def AI_drop(self):
        x, y = self.findBestChess(self._board, self.value)
        point = Point(x, y)
        return point

    pass
