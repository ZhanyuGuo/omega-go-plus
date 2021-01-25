from flask import Flask, jsonify, request
from BoardBasics import *
import sqlite3

# FLASK
app = Flask(__name__)

# DATABASE
db = "test.db"
conn = sqlite3.connect(db, check_same_thread=False)
c = conn.cursor()
try:
    c.execute("DROP TABLE agent")
finally:
    c.execute('''CREATE TABLE agent
               (id          INT               NOT NULL,
               playerid    CHAR(16)          NOT NULL,
               x           INT               NOT NULL,
               y           INT               NOT NULL,
               win         INT               NOT NULL,
               move_count  INT               NOT NULL,
               round      INT               NOT NULL);''')
    print("Create {} successfully".format(db))
    pass


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

"""
    Globals
"""
chessman_list = []  # Player list
move_history = []   # Move history
state = 0           # Game state
newID = 0           # Player id
count = 0           # Step count
round_ = 1

# Init a Board
board = Board(LINES)

# Some data
board_dict_send = {'board': board,
                   'id': '1',
                   'playerid': 'black',  # runner
                   'win': 0,
                   'newvalue': 0,  # INIT=0（尚未开始），ACTIVE（已开始）=1，IDLE（空闲）=2，OVER（结束）=3
                   'lastX': -1,
                   'lastY': -1,
                   'move_count': 1}


# 主页
@app.route('/')
def index():
    return jsonify('Hello OmegaGo!')


# 返回游戏状态
@app.route('/rest/play', methods=['GET'])
def getRestPlay():
    global state

    return jsonify(state)


# 设置游戏状态（没用到）
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


# 返回游戏报告
@app.route('/rest/play/report', methods=['GET'])
def getRestPlayReport():
    winner = board.winner

    if winner is None:
        report = "Game is underway..."
    else:
        winner_name = winner.name
        if winner_name in ['black', 'white', 'yellow']:
            report = f"Game over, {winner} win..."
        else:
            report = "error！"
            pass
        pass

    return jsonify(
        {'report': report}
    )


# 玩家管理
@app.route('/rest/player', methods=['GET', 'POST'])
def getRestPlayer():
    global newID

    send = dict()
    if request.method == 'GET':
        for chessman in chessman_list:
            send[chessman.name] = chessman.id
            pass

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


# 返回指定ID的玩家信息
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


rst_count = 0
num = 0


# 当前棋盘管理
@app.route('/rest/board', methods=['GET', 'POST'])
def getRestBoard():
    global board, rst_count, state, num, move_history, newID, count, newID, round_

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
        new_playerid = request.form['color']

        if new_x == -1 or new_x == -2:
            if new_x == -2:
                newID -= 1
                i = 0
                for man in chessman_list:
                    if man.id == new_id:
                        break
                        pass
                    i += 1
                    pass
                chessman_list.pop(i)
                pass

            if rst_count < board.players - 1:
                rst_count += 1
                state = 2
                return jsonify(
                    {
                        'succ': '-1 -1 joint successfully',
                        'msg': 'waiting...'
                    }
                )

            rst_count = 0
            state = 0
            board = Board(LINES)
            board.players = newID
            num = 0
            move_history = []
            round_ += 1
            # c.execute("DROP TABLE agent")
            # c.execute('''CREATE TABLE agent
            #            (id         INT               NOT NULL,
            #            playerid    CHAR(16)          NOT NULL,
            #            x           INT               NOT NULL,
            #            y           INT               NOT NULL,
            #            win         INT               NOT NULL,
            #            move_count  INT               NOT NULL);''')
            return jsonify(
                {
                    'succ': '-1 -1 joint successfully',
                    'msg': 'all rerun'
                }
            )

        point = Point(new_x, new_y)
        if board.canDrop(point):
            board.winner = board.drop(board.cur_runner, point)
            num = num + 1
            move = {
                'num': num,
                'id': new_id,
                'x': new_x,
                'y': new_y
            }
            move_history.append(move)
            win = 0 if board.winner is None else 1
            c.execute("INSERT INTO agent (id,playerid,x,y,win,move_count,round) \
                      VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(new_id, new_playerid, new_x, new_y, win, num, round_))
            conn.commit()

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


@app.route('/rest/regret', methods=['GET'])
def regret():
    global board, num

    point = board.history.pop(-1)
    board = board.getBoard()
    board[point.y][point.x] = 0
    board.setBoard(board)

    point = board.history.pop(-1)
    board = board.getBoard()
    board[point.y][point.x] = 0
    board.setBoard(board)

    board.last = board.history[-1]

    if num > 2:
        c.execute("DELETE from agent where move_count=%s;" % str(num))
        c.execute("DELETE from agent where move_count=%s;" % str(num - 1))
        conn.commit()
        num -= 2
        pass
    pass


# @app.route('/rest/regret', methods=['GET'])
# def regret():
#     global board, num
#
#     if num > 2:
#         last1 = c.execute("SELECT * from agent where move_count=%s" % str(num))
#         last2 = c.execute("SELECT * from agent where move_count=%s" % str(num - 1))
#         for row in last1:
#             last1x = row[2]
#             last1y = row[3]
#             pass
#
#         for row in last2:
#             last2x = row[2]
#             last2y = row[3]
#             pass
#
#         last1_point = Point(last1x, last1y)
#         last2_point = Point(last2x, last2y)
#
#         board = board.getBoard()
#         board[last1_point.y][last1_point.x] = 0
#         board.setBoard(board)
#
#         board = board.getBoard()
#         board[last2_point.y][last2_point.x] = 0
#         board.setBoard(board)
#
#         # board.last = board.history[-1]
#
#         c.execute("DELETE from agent where move_count=%s;" % str(num))
#         c.execute("DELETE from agent where move_count=%s;" % str(num - 1))
#         conn.commit()
#         num -= 2
#         pass
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
    pass


# @app.route('/rest/action/last', methods=['GET'])
# def getRestActionLast():
#     global num
#
#     if num:
#         last = c.execute("SELECT * FROM agent where move_count=%d;" % num)
#         send = dict()
#         for row in last:
#             send['playerid'] = last[0]
#             send['x'] = last[2]
#             send['y'] = last[3]
#             pass
#         return jsonify(send)
#     else:
#         return jsonify('No Stone has been dropped...')
#     pass


# 获取历史走子序列的长度
@app.route('/rest/action/count', methods=['GET'])
def getRestActionCount():
    global board

    return jsonify(len(board.history))


# # 获取历史走子序列的长度
# @app.route('/rest/action/count', methods=['GET'])
# def getRestActionCount():
#     global num
#
#     return jsonify(num)


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


# 获取指定步的历史走子信息
# @app.route('/rest/action/<int:value>', methods=['GET'])
# def getRestActionValue(value):
#     if value <= num:
#         move2 = c.execute("SELECT * FROM agent where move_count=%d" % value)
#         for row in move2:
#             rlt_id = row[0]
#             rlt_x = row[2]
#             rlt_y = row[3]
#             pass
#
#         return jsonify(
#             {
#                 'id': rlt_id,
#                 'x': rlt_x,
#                 'y': rlt_y
#             }
#         )
#     return jsonify('error')


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

    return jsonify(send)


# 获取历史走子信息
# /rest/action?stepfrom=<value1>&stepto=<value2>
# @app.route('/rest/action', methods=['GET'])
# def getRestActionStep():
#
#     value1 = int(request.args.get('stepfrom'))
#     value2 = int(request.args.get('stepto'))
#
#     if 1 <= value1 <= num:
#         if value1 < value2 <= num:
#             send = c.execute("SELECT * FROM agent where move_count>=%d AND move_count<=%d" % (value1, value2))
#             pass
#     else:
#         send = {}
#         pass
#
#     return jsonify(send)


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
    app.run(port='5000')
    # app.run(host='0.0.0.0', port='5000')

