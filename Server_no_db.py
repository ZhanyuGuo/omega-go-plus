from flask import Flask, jsonify, request
from BoardBasics import *
import ChessAI_flask
import ChessAI_flask_gst

app = Flask(__name__)
# ai = ChessAI_flask.ChessAI(LINES)
blackscore, whitescore, whitescore1, yellowscore1 = 0, 0, 0, 0


class ChessmanFlask(Chessman):
    """
    Define a Chessman's Properties in flask.
    """
    def __init__(self, name, value, color, id_, ip):
        """
        Init a Chessman in flask

        :param name: Chessman's name -> str()
        :param value: Chessman's value -> int()
        :param color: Chessman's color -> QColor()
        :param id_: Chessman's id -> int()
        :param ip: Chessman's ip -> str()
        """
        super(ChessmanFlask, self).__init__(name, value, color)
        self.id = id_
        self.ip = ip
        pass

    pass


# EMPTY_CHESSMAN = Chessman('empty', 0, (128, 128, 128), '0.0.0.0')
# BLACK_CHESSMAN = Chessman('black', 1, (45, 45, 45), '100.21.564.23')
# WHITE_CHESSMAN = Chessman('white', 2, (219, 219, 219), '120.17.585.42')

# 放置玩家列表
chessman_list = []

# 初始棋盘
board = Board(LINES)
board_send = {
    'board': board.getBoard(),
    'runner': 'black',
    'win': 0,
    'state': 0,  # INIT=0（尚未开始），ACTIVE（已开始）=1，IDLE（空闲）=2，OVER（结束）=3
    'lastX': -1,
    'lastY': -1
}

move_history = []

win_times = [0] * 3
win = 0
_win_ = 0
state = 0
newID = 0

x = 0
y = 0


@app.route('/')
def index():
    return jsonify('Hello OmegaGo')


# 当前棋局管理
@app.route('/rest/play', methods=['GET'])
def getRestPlay():
    return jsonify(state)

# def getPlay():
#     global win, state, board_send
#
#     if boardClass.winner == BLACK_CHESSMAN:
#         win = 1
#     elif boardClass.winner == WHITE_CHESSMAN:
#         win = 2
#     else:
#         win = 0
#         pass
#
#     board_send['board'] = boardClass.getBoard()
#     board_send['runner'] = boardClass.cur_runner.name
#     board_send['win'] = win
#     board_send['state'] = state
#     board_send['lastX'] = board_rev['x']
#     board_send['lastY'] = board_rev['y']
#     return board_send


@app.route('/rest/play/state', methods=['GET'])
def getRestPlayState():
    global state

    state = int(request.args.get('newvalue'))
    if state == 0:
        rlt = "INIT"
    elif state == 1:
        rlt = "ACTIVE"
    elif state == 2:
        rlt = "IDLE"
    elif state == 3:
        rlt = "OVER"
    else:
        rlt = "ERROR"
        pass

    return jsonify(rlt)


# @app.route('/rest/play/report', methods=['GET'])
# def getRestPlayReport():
#     winner = board.winner
#
#     if winner is None:
#         report = "Game is underway..."
#     else:
#         winner_name = winner.name
#         if winner_name in ['black', 'white', 'yellow']:
#             report = f"Game over, {winner} win..."
#         else:
#             report = "error！"
#             pass
#         pass
#
#     return jsonify(
#         {'report': report}
#     )

@app.route('/rest/play/report', methods=['GET'])
def getRestPlayReport():
    if newID == 2:
        t = win_times[0:2]
        if blackscore + whitescore != 0:
            t.append(blackscore / (blackscore + whitescore) * 100)
        else:
            t.append(50)
            pass
        t.append(0)
        t.append(0)
        t.append(0)
        t.append(0)
        # t = [x, x, x]

    elif newID == 3:
        t = win_times[0:3]  # t = [x, x, x, y, y]
        if blackscore + whitescore1 + yellowscore1 != 0:
            t.append(blackscore/(blackscore + whitescore1 + yellowscore1)*100)
            t.append(whitescore1/(blackscore + whitescore1 + yellowscore1)*100)
            pass
        else:
            t.append(50)
            t.append(50)
            pass
    else:
        t = [0]*10

    return jsonify(t)


@app.route('/rest/player', methods=['GET', 'POST'])
def getRestPlayer():
    global newID

    send = dict()
    if request.method == 'GET':
        for chessman in chessman_list:
            send[chessman.name] = chessman.id

        return jsonify(send)

    elif request.method == 'POST':
        name = request.form['color']
        if name == 'black':
            color = BLACK_STONE_COLOR
            value = 1
        elif name == 'white':
            color = WHITE_STONE_COLOR
            value = 2
        elif name == 'yellow':
            color = YELLOW_STONE_COLOR
            value = 3
        else:
            return 'error: color'

        newID = newID + 1
        board.players = newID
        # 注意，value和id取同一个值，方便处理
        newChessman = ChessmanFlask(name, value, color, value, request.form['ip'])
        chessman_list.append(newChessman)
        return jsonify(
            {
                "succ": '{} joint successfully'.format(name),
                "msg": 'number of players: {}'.format(newID)
            }
        )
    pass


@app.route('/rest/player/<int:id_>', methods=['GET'])
def getRestPlayerID(id_):
    for Chessman_agent_item in chessman_list:
        if Chessman_agent_item.id == id_:
            return jsonify(
                {
                    'name': Chessman_agent_item.name,
                    'value': Chessman_agent_item.value,
                    'id': Chessman_agent_item.id,
                    'IP': Chessman_agent_item.ip
                }
            )


count = 0
num = 0


# 当前棋盘管理
@app.route('/rest/board', methods=['GET', 'POST'])
def getRestBoard():
    global blackscore, whitescore, whitescore1, yellowscore1, board, count, state, num, move_history, newID, chessman_list, newID

    if request.method == 'GET':
        return jsonify(
            {
                "board": board.getBoard(),
                "width": LINES,
                "height": LINES
            }
        )
    elif request.method == 'POST':
        new_id = int(request.form['id'])
        new_x = int(request.form['x'])
        new_y = int(request.form['y'])
        new_color = request.form['color']

        if new_x == -1 or new_x == -2:
            if new_x == -2:
                # newID -= 1
                i = 0
                for man in chessman_list:
                    if man.id == new_id:
                        break
                        pass
                    i += 1
                    pass
                chessman_list.pop(i)
                pass

            if count < newID - 1:
                count += 1
                state = 2
                return jsonify(
                    {
                        'succ': '-1 -1 joint successfully',
                        'msg': 'waiting...'
                    }
                )

            newID = len(chessman_list)
            count = 0
            state = 0
            board = Board(LINES)
            board.players = newID
            num = 0
            move_history = []

            return jsonify(
                {
                    'succ': '-1 -1 joint successfully',
                    'msg': 'all rerun'
                }
            )

        point = Point(new_x, new_y)
        if board.canDrop(point):
            board.winner = board.drop(board.cur_runner, point)
            if board.winner:
                win_times[board.winner.value - 1] += 1
                pass

            if newID == 2:
                ai = ChessAI_flask.ChessAI(LINES)
                if board.cur_runner == WHITE_CHESSMAN:
                    blackscore, whitescore = ai.evaluate(board.getBoard(), BLACK_CHESSMAN.value)
                else:
                    whitescore, blackscore = ai.evaluate(board.getBoard(), WHITE_CHESSMAN.value)
                    pass
            elif newID == 3:
                ai = ChessAI_flask_gst.ChessAI(LINES)
                if board.cur_runner == BLACK_CHESSMAN:
                    whitescore1, yellowscore1, blackscore = ai.evaluate(board.getBoard(), WHITE_CHESSMAN.value)
                elif board.cur_runner == WHITE_CHESSMAN:
                    yellowscore1, blackscore, whitescore1 = ai.evaluate(board.getBoard(), YELLOW_CHESSMAN.value)
                else:
                    blackscore, whitescore1, yellowscore1 = ai.evaluate(board.getBoard(), BLACK_CHESSMAN.value)

            num = num + 1
            move = {
                'num': num,
                'id': new_id,
                'x': new_x,
                'y': new_y
            }
            move_history.append(move)

        if board.winner is not None:
            state = 3
            pass

        board.cur_runner = board.getNextRunner(board.cur_runner)

        return jsonify(
            {
                "succ": 'id: {} post successfully'.format(new_id),
                "msg": 'current {}'.format(board.cur_runner.name)
            }
        )


# @app.route('/rest/regret', methods=['GET'])
# def regret():
#     point = boardClass.history.pop(-1)
#     board = boardClass.getBoard()
#     board[point.y][point.x] = 0
#     boardClass.setBoard(board)
#
#     point = boardClass.history.pop(-1)
#     board = boardClass.getBoard()
#     board[point.y][point.x] = 0
#     boardClass.setBoard(board)
#
#     boardClass.last = boardClass.history[-1]
#     pass


# 走子管理
@app.route('/rest/action/last', methods=['GET'])
def getRestActionLast():
    if num:
        last = move_history[-1]
        send = dict()
        send['playerid'] = last['id']
        send['x'] = last['x']
        send['y'] = last['y']
        return jsonify(send)
    else:
        return jsonify('No Stone has been dropped...')


# 获取历史走子序列的长度
@app.route('/rest/action/count', methods=['GET'])
def getRestActionCount():
    return jsonify(len(board.history))


# 获取指定步的历史走子信息
@app.route('/rest/action/<int:value>', methods=['GET'])
def getRestActionValue(value):
    if value <= num:
        move = move_history[value - 1]
        rlt_id = move['id']
        rlt_x = move['x']
        rlt_y = move['y']
        return jsonify(
            {
                'id': rlt_id,
                'x': rlt_x,
                'y': rlt_y
            }
        )
    return jsonify('error')


# 获取历史走子信息
# /rest/action?stepfrom=<value1>&stepto=<value2>
@app.route('/rest/action', methods=['GET'])
def getRestActionStep():

    value1 = int(request.args.get('stepfrom'))
    value2 = int(request.args.get('stepto'))

    if value1 <= num:
        if value2 <= num:
            send = move_history[value1 - 1:value2]
        else:
            send = move_history[value1 - 1:-1]
            pass
    else:
        send = {}
        pass

    # for move_history_item in move_history:
    #     if move_history_item['num'] >= value1:
    #         if move_history_item['num'] != value2:
    #             print(move_history_item['num'])
    #             print(move_history_item['id'])
    #             print(move_history_item['x'])
    #             print(move_history_item['y'])
    #             print('\r')
    #         elif move_history_item['num'] == value2:
    #             return 'Stop here!'
    return jsonify(send)


def getLocalIP():
    """
    Get local IP.

    :return: ip -> str()
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
        pass
    return ip
    pass


if __name__ == '__main__':
    print("------------------------------")
    print("Server's IP: ", getLocalIP())
    print("------------------------------")
    # app.run(port='5000')
    app.run(host='0.0.0.0', port='5000')

