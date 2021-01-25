#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/25 13:09
# @Author  : Zhanyu Guo
# @Email   : 942568052@qq.com
# @File    : ChessAI3.py
# @Software: PyCharm
from enum import IntEnum
from random import randint
import time

AI_SEARCH_DEPTH = 3
AI_LIMITED_MOVE_NUM = 5


class CHESS_TYPE(IntEnum):
    NONE = 0,
    SLEEP_TWO = 1,
    LIVE_TWO = 2,
    SLEEP_THREE = 3
    LIVE_THREE = 4,
    CHONG_FOUR = 5,
    LIVE_FOUR = 6,
    LIVE_FIVE = 7,
    pass


class MAP_ENTRY_TYPE(IntEnum):
    MAP_EMPTY = 0,
    MAP_PLAYER_ONE = 1,
    MAP_PLAYER_TWO = 2,
    MAP_PLAYER_THREE = 3,  # 新增黄子
    MAP_NONE = 4,  # out of map range
    pass


CHESS_TYPE_NUM = 8

FIVE = CHESS_TYPE.LIVE_FIVE.value
FOUR, THREE, TWO = CHESS_TYPE.LIVE_FOUR.value, CHESS_TYPE.LIVE_THREE.value, CHESS_TYPE.LIVE_TWO.value
SFOUR, STHREE, STWO = CHESS_TYPE.CHONG_FOUR.value, CHESS_TYPE.SLEEP_THREE.value, CHESS_TYPE.SLEEP_TWO.value

SCORE_MAX = 0x7fffffff
SCORE_MIN = -1 * SCORE_MAX
SCORE_FIVE, SCORE_FOUR, SCORE_SFOUR = 100000, 10000, 1000
SCORE_THREE, SCORE_STHREE, SCORE_TWO, SCORE_STWO = 100, 10, 8, 2


class ChessAI:
    def __init__(self, chess_len):
        self.len = chess_len
        # [horizon, vertical, left diagonal, right diagonal]
        self.record = [[[0, 0, 0, 0] for x in range(chess_len)] for y in range(chess_len)]
        self.count = [[0 for x in range(CHESS_TYPE_NUM)] for i in range(3)]

    def reset(self):
        for y in range(self.len):
            for x in range(self.len):
                for i in range(4):
                    self.record[y][x][i] = 0
        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

    def click(self, map, x, y, turn):
        map.click(x, y, turn)

    def isWin(self, board, turn):
        return self.evaluate(board, turn, True)

    # evaluate score of point, to improve pruning efficiency
    def evaluatePointScore(self, board, x, y, mine, opponent1, opponent2):  # 在空闲点下子所得三个分数  # 某一落点的分数
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

        board[y][x] = mine
        self.evaluatePoint(board, x, y, mine, opponent1, opponent2, self.count[mine - 1])
        mine_count = self.count[mine - 1]
        board[y][x] = opponent1
        self.evaluatePoint(board, x, y, opponent1, opponent2, mine, self.count[opponent1 - 1])
        opponent1_count = self.count[opponent1 - 1]
        board[y][x] = opponent2
        self.evaluatePoint(board, x, y, opponent2, mine, opponent1, self.count[opponent2 - 1])
        opponent2_count = self.count[opponent2 - 1]
        board[y][x] = 0

        mscore = self.getPointScore(mine_count)
        o1score = self.getPointScore(opponent1_count)
        o2score = self.getPointScore(opponent2_count)

        return (mscore, o1score, o2score)

    # check if has a none empty position in it's radius range
    def hasNeighbor(self, board, x, y, radius):  # 不用改
        start_x, end_x = (x - radius), (x + radius)
        start_y, end_y = (y - radius), (y + radius)

        for i in range(start_y, end_y + 1):
            for j in range(start_x, end_x + 1):
                if i >= 0 and i < self.len and j >= 0 and j < self.len:
                    if board[i][j] != 0:
                        return True
        return False

    # get all positions near chess
    def genmove(self, board, turn):
        fives = []
        mfours, o1fours, o2fours = [], [], []
        msfours, o1sfours, o2sfours = [], [], []
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            mine = 1
            opponent1 = 2
            opponent2 = 3
        elif turn == MAP_ENTRY_TYPE.MAP_PLAYER_TWO:  # 新增黄子
            mine = 2
            opponent1 = 3
            opponent2 = 1
        else:
            mine = 3
            opponent1 = 1
            opponent2 = 2

        moves = []
        radius = 1

        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == 0 and self.hasNeighbor(board, x, y, radius):
                    mscore, o1score, o2score = self.evaluatePointScore(board, x, y, mine, opponent1, opponent2)
                    point = (max(mscore, o1score, o2score), x, y)

                    if mscore >= SCORE_FIVE or o1score >= SCORE_FIVE or o2score >= SCORE_FIVE:
                        fives.append(point)
                    elif mscore >= SCORE_FOUR:
                        mfours.append(point)
                    elif o1score >= SCORE_FOUR:
                        o1fours.append(point)
                    elif o2score >= SCORE_FOUR:
                        o2fours.append(point)
                    elif mscore >= SCORE_SFOUR:
                        msfours.append(point)
                    elif o1score >= SCORE_SFOUR:
                        o1sfours.append(point)
                    elif o2score >= SCORE_SFOUR:
                        o2sfours.append(point)

                    moves.append(point)

        if len(fives) > 0: return fives

        if len(mfours) > 0: return mfours

        if len(o1fours) > 0:
            if len(msfours) == 0:
                return o1fours
            else:
                return o1fours + msfours
        if len(o2fours) > 0:
            if len(msfours) == 0:
                return o2fours
            else:
                return o2fours + msfours

        moves.sort(reverse=True)  # 将point进行降序排列

        # FIXME: decrease think time: only consider limited moves with higher scores
        if self.maxdepth > 2 and len(moves) > AI_LIMITED_MOVE_NUM:
            moves = moves[:AI_LIMITED_MOVE_NUM]
        return moves

    def __search(self, board, turn, depth, alpha=SCORE_MIN, beta=SCORE_MAX):
        score = self.evaluate(board, turn)
        if depth <= 0 or abs(score) >= SCORE_FIVE:
            return score

        moves = self.genmove(board, turn)
        bestmove = None
        self.alpha += len(moves)  # print出来检验的作用

        # if there are no moves, just return the score
        if len(moves) == 0:
            return score

        for _, x, y in moves:
            board[y][x] = turn

            if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
                op_turn = MAP_ENTRY_TYPE.MAP_PLAYER_TWO
            elif turn == MAP_ENTRY_TYPE.MAP_PLAYER_TWO:  # 新增黄子
                op_turn = MAP_ENTRY_TYPE.MAP_PLAYER_THREE
            else:
                op_turn = MAP_ENTRY_TYPE.MAP_PLAYER_ONE

            score = - self.__search(board, op_turn, depth - 1, -beta, -alpha)

            board[y][x] = 0
            # self.belta += 1
            self.beta += 1  # print出来检验的作用

            # alpha/beta pruning
            if score > alpha:
                alpha = score
                bestmove = (x, y)
                if alpha >= beta:
                    break

        if depth == self.maxdepth and bestmove:
            self.bestmove = bestmove

        print('(%d, %d), score[%d] alpha[%d] belta[%d]' % (x, y, score, alpha, beta))

        return alpha

    def search(self, board, turn, depth=AI_SEARCH_DEPTH):
        self.maxdepth = depth
        self.bestmove = None
        score = self.__search(board, turn, depth)
        print("\r\n")
        if self.bestmove is not None:
            x, y = self.bestmove
        else:
            x, y = self.len//2, self.len//2
        return score, x, y

    def findBestChess(self, board, turn):
        time1 = time.time()
        self.alpha = 0
        # self.belta = 0
        self.beta = 0
        score, x, y = self.search(board, turn, AI_SEARCH_DEPTH)
        time2 = time.time()
        # print('time[%.2f] (%d, %d), score[%d] alpha[%d] belta[%d]' % ((time2 - time1), x, y, score, self.alpha, self.beta))
        return (x, y)

    def getPointScore(self, count):
        score = 0
        if count[FIVE] > 0:
            return SCORE_FIVE

        if count[FOUR] > 0:
            return SCORE_FOUR

        # FIXME: the score of one chong four and no live three should be low, set it to live three
        if count[SFOUR] > 1:
            score += count[SFOUR] * SCORE_SFOUR
        elif count[SFOUR] > 0 and count[THREE] > 0:
            score += count[SFOUR] * SCORE_SFOUR
        elif count[SFOUR] > 0:
            score += SCORE_THREE

        if count[THREE] > 1:
            score += 5 * SCORE_THREE
        elif count[THREE] > 0:
            score += SCORE_THREE

        if count[STHREE] > 0:
            score += count[STHREE] * SCORE_STHREE
        if count[TWO] > 0:
            score += count[TWO] * SCORE_TWO
        if count[STWO] > 0:
            score += count[STWO] * SCORE_STWO

        return score

    # calculate score, FIXME: May Be Improved
    def getScore(self, mine_count, opponent1_count, opponent2_count):
        mscore, o1score, o2score = 0, 0, 0
        if mine_count[FIVE] > 0:
            return (SCORE_FIVE, 0, 0)
        if opponent1_count[FIVE] > 0:
            return (0, SCORE_FIVE, 0)
        if opponent2_count[FIVE] > 0:
            return (0, 0, SCORE_FIVE)

        if mine_count[SFOUR] >= 2:
            mine_count[FOUR] += 1
        if opponent1_count[SFOUR] >= 2:
            opponent1_count[FOUR] += 1
        if opponent2_count[SFOUR] >= 2:
            opponent2_count[FOUR] += 1

        if mine_count[FOUR] > 0:
            return (9050, 0, 0)
        if mine_count[SFOUR] > 0:
            return (9040, 0, 0)

        if opponent1_count[FOUR] > 0:
            return (0, 9030, 0)
        if opponent2_count[FOUR] > 0:
            return (0, 0, 9030)
        if opponent1_count[SFOUR] > 0 and opponent1_count[THREE] > 0:
            return (0, 9020, 0)
        if opponent2_count[SFOUR] > 0 and opponent2_count[THREE] > 0:
            return (0, 0, 9020)

        if mine_count[THREE] > 0 and opponent1_count[SFOUR] == 0:
            return (9010, 0, 0)
        if mine_count[THREE] > 0 and opponent2_count[SFOUR] == 0:
            return (9010, 0, 0)

        if (opponent1_count[THREE] > 1 and mine_count[THREE] == 0 and mine_count[STHREE] == 0):
            return (0, 9000, 0)
        if (opponent2_count[THREE] > 1 and mine_count[THREE] == 0 and mine_count[STHREE] == 0):
            return (0, 0, 9000)

        if opponent1_count[SFOUR] > 0:
            o1score += 400
        if opponent2_count[SFOUR] > 0:
            o2score += 400

        if mine_count[THREE] > 1:
            mscore += 500
        elif mine_count[THREE] > 0:
            mscore += 100

        if opponent1_count[THREE] > 1:
            o1score += 2000
        elif opponent1_count[THREE] > 0:
            o1score += 400
        if opponent2_count[THREE] > 1:
            o2score += 2000
        elif opponent2_count[THREE] > 0:
            o2score += 400

        if mine_count[STHREE] > 0:
            mscore += mine_count[STHREE] * 10
        if opponent1_count[STHREE] > 0:
            o1score += opponent1_count[STHREE] * 10
        if opponent2_count[STHREE] > 0:
            o2score += opponent2_count[STHREE] * 10

        if mine_count[TWO] > 0:
            mscore += mine_count[TWO] * 6
        if opponent1_count[TWO] > 0:
            o1score += opponent1_count[TWO] * 6
        if opponent2_count[TWO] > 0:
            o2score += opponent2_count[TWO] * 6

        if mine_count[STWO] > 0:
            mscore += mine_count[STWO] * 2
        if opponent1_count[STWO] > 0:
            o1score += opponent1_count[STWO] * 2
        if opponent2_count[STWO] > 0:
            o2score += opponent2_count[STWO] * 2

        return (mscore, o1score, o2score)

    def evaluate(self, board, turn, checkWin=False):  # 评价当前棋局分数
        self.reset()

        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            mine = 1
            opponent1 = 2
            opponent2 = 3
        elif turn == MAP_ENTRY_TYPE.MAP_PLAYER_TWO:
            mine = 2
            opponent1 = 3
            opponent2 = 1
        else:
            mine = 3
            opponent1 = 1
            opponent2 = 2

        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == mine:
                    self.evaluatePoint(board, x, y, mine, opponent1, opponent2)  # 新增黄子
                elif board[y][x] == opponent1:
                    self.evaluatePoint(board, x, y, opponent1, opponent2, mine)
                else:
                    self.evaluatePoint(board, x, y, opponent2, mine, opponent1)

        mine_count = self.count[mine - 1]
        opponent1_count = self.count[opponent1 - 1]
        opponent2_count = self.count[opponent2 - 1]
        if checkWin:
            return mine_count[FIVE] > 0
        else:
            mscore, o1score, o2score = self.getScore(mine_count, opponent1_count, opponent2_count)  # 新增黄子
            return mscore - 0.6*o1score - 0.4*o2score  # 下下家的比重低于下家

    def evaluatePoint(self, board, x, y, mine, opponent1, opponent2, count=None):
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        ignore_record = True
        if count is None:
            count = self.count[mine - 1]
            ignore_record = False
        for i in range(4):
            if self.record[y][x][i] == 0 or ignore_record:
                self.analysisLine(board, x, y, i, dir_offset[i], mine, opponent1, opponent2, count)  # 新增黄子

    # line is fixed len 9: XXXXMXXXX
    def getLine(self, board, x, y, dir_offset, mine, opponent1, opponent2):  # 排查某一行/列/对角线的九子
        line = [0 for i in range(9)]

        tmp_x = x + (-5 * dir_offset[0])
        tmp_y = y + (-5 * dir_offset[1])
        for i in range(9):
            tmp_x += dir_offset[0]
            tmp_y += dir_offset[1]
            if (tmp_x < 0 or tmp_x >= self.len or
                    tmp_y < 0 or tmp_y >= self.len):
                line[i] = MAP_ENTRY_TYPE.MAP_NONE  # set out of range as opponent chess
            else:
                line[i] = board[tmp_y][tmp_x]

        return line

    def analysisLine(self, board, x, y, dir_index, dir, mine, opponent1, opponent2, count):
        # record line range[left, right] as analysized
        def setRecord(self, x, y, left, right, dir_index, dir_offset):
            tmp_x = x + (-5 + left) * dir_offset[0]
            tmp_y = y + (-5 + left) * dir_offset[1]
            for i in range(left, right + 1):
                tmp_x += dir_offset[0]
                tmp_y += dir_offset[1]
                self.record[tmp_y][tmp_x][dir_index] = 1

        empty = MAP_ENTRY_TYPE.MAP_EMPTY.value
        left_idx, right_idx = 4, 4

        line = self.getLine(board, x, y, dir, mine, opponent1, opponent2)

        opponent = [opponent1, opponent2]

        while right_idx < 8:
            if line[right_idx + 1] != mine:  # 查由中间出发，右边的M最大拓展到right_idx
                break
            right_idx += 1
        while left_idx > 0:
            if line[left_idx - 1] != mine:  # 查由中间出发，左边的M最大拓展到left_idx
                break
            left_idx -= 1

        left_range, right_range = left_idx, right_idx
        while right_range < 8:
            if line[right_range + 1] in opponent:  # 查由右边的M最大拓展到right_idx出发，判断再往后的是空还是对手，遇到对手退出
                break
            right_range += 1
        while left_range > 0:
            if line[left_range - 1] in opponent:  # 查由左边的M最大拓展到left_idx出发，判断再往后的是空还是对手，遇到对手退出
                break
            left_range -= 1

        chess_range = right_range - left_range + 1
        if chess_range < 5:
            setRecord(self, x, y, left_range, right_range, dir_index, dir)
            return CHESS_TYPE.NONE

        setRecord(self, x, y, left_idx, right_idx, dir_index, dir)

        m_range = right_idx - left_idx + 1  # M的长度范围

        # M:mine chess, P:opponent chess or out of range, X: empty
        if m_range >= 5:
            count[FIVE] += 1

        # Live Four : XMMMMX
        # Chong Four : XMMMMP, PMMMMX
        if m_range == 4:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                left_empty = True
            if line[right_idx + 1] == empty:
                right_empty = True
            if left_empty and right_empty:
                count[FOUR] += 1
            elif left_empty or right_empty:
                count[SFOUR] += 1

        # Chong Four : MXMMM, MMMXM, the two types can both exist
        # Live Three : XMMMXX, XXMMMX
        # Sleep Three : PMMMX, XMMMP, PXMMMXP
        if m_range == 3:
            left_empty = right_empty = False
            left_four = right_four = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:  # MXMMM
                    setRecord(self, x, y, left_idx - 2, left_idx - 1, dir_index, dir)
                    count[SFOUR] += 1
                    left_four = True
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:  # MMMXM
                    setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index, dir)
                    count[SFOUR] += 1
                    right_four = True
                right_empty = True

            if left_four or right_four:
                pass
            elif left_empty and right_empty:
                if chess_range > 5:  # XMMMXX, XXMMMX
                    count[THREE] += 1
                else:  # PXMMMXP
                    count[STHREE] += 1
            elif left_empty or right_empty:  # PMMMX, XMMMP
                count[STHREE] += 1

        # Chong Four: MMXMM, only check right direction
        # Live Three: XMXMMX, XMMXMX the two types can both exist
        # Sleep Three: PMXMMX, XMXMMP, PMMXMX, XMMXMP
        # Live Two: XMMX
        # Sleep Two: PMMX, XMMP
        if m_range == 2:
            left_empty = right_empty = False
            left_three = right_three = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    setRecord(self, x, y, left_idx - 2, left_idx - 1, dir_index, dir)
                    if line[left_idx - 3] == empty:
                        if line[right_idx + 1] == empty:  # XMXMMX
                            count[THREE] += 1
                        else:  # XMXMMP
                            count[STHREE] += 1
                        left_three = True
                    elif line[left_idx - 3] in opponent:  # PMXMMX
                        if line[right_idx + 1] == empty:
                            count[STHREE] += 1
                            left_three = True

                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if line[right_idx + 3] == mine:  # MMXMM
                        setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index, dir)
                        count[SFOUR] += 1
                        right_three = True
                    elif line[right_idx + 3] == empty:
                        # setRecord(self, x, y, right_idx+1, right_idx+2, dir_index, dir)
                        if left_empty:  # XMMXMX
                            count[THREE] += 1
                        else:  # PMMXMX
                            count[STHREE] += 1
                        right_three = True
                    elif left_empty:  # XMMXMP
                        count[STHREE] += 1
                        right_three = True

                right_empty = True

            if left_three or right_three:
                pass
            elif left_empty and right_empty:  # XMMX
                count[TWO] += 1
            elif left_empty or right_empty:  # PMMX, XMMP
                count[STWO] += 1

        # Live Two: XMXMX, XMXXMX only check right direction
        # Sleep Two: PMXMX, XMXMP
        if m_range == 1:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    if line[left_idx - 3] == empty:
                        if line[right_idx + 1] in opponent:  # XMXMP
                            count[STWO] += 1
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if line[right_idx + 3] == empty:
                        if left_empty:  # XMXMX
                            # setRecord(self, x, y, left_idx, right_idx+2, dir_index, dir)
                            count[TWO] += 1
                        else:  # PMXMX
                            count[STWO] += 1
                elif line[right_idx + 2] == empty:
                    if line[right_idx + 3] == mine and line[right_idx + 4] == empty:  # XMXXMX
                        count[TWO] += 1

        return CHESS_TYPE.NONE
