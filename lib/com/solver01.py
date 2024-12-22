# !/usr/bin/env python
# coding: utf-8
import base64
import datetime
import json
import random
import urllib.parse
from typing import Tuple
from lib.com.iobase import IOBase
from copy import deepcopy

ROW_AMOUNT = 6
COL_AMOUNT = 8
ORDZ_BOMB = "■"
POSSIBLE_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DEMO_MAP = [[3, 1, 2, 0, 3, 1, 2, 4],
            [1, 3, 4, 1, 1, 2, 3, 2],
            [4, 2, 0, 3, 0, 1, 3, 0],
            [4, 1, 3, 0, 3, 3, 2, 1],
            [1, 3, 1, 3, 3, 4, 3, 0],
            [2, 3, 0, 1, 0, 4, 0, 4]]


def base36encoderequiredstr() -> str:
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    generated_characters = ''.join(random.choice(alphabet) for _ in range(10))
    return f"1.{generated_characters}"


def simple_check_explodes(map_matrix: list[list]):
    results = []

    for r in range(ROW_AMOUNT):
        i = 0
        j = 1
        while j < COL_AMOUNT:
            if map_matrix[r][i] != map_matrix[r][j]:
                if j - i >= 3:
                    for m in range(i, j):
                        results.append((r, m))
                i = j
            j += 1

    for r in range(COL_AMOUNT):
        i = 0
        j = 1
        while j < ROW_AMOUNT:
            # print(r, i, j)
            if map_matrix[i][r] != map_matrix[j][r]:
                if j - i >= 3:
                    for m in range(i, j):
                        results.append((m, r))
                i = j
            j += 1

    return results


def fill04_checker(j, pre_row) -> bool:
    if len(pre_row) == 0:
        return False
    for K in pre_row:
        if isinstance(K, Tuple) is True:
            (jj, _, r) = K
            if jj == j:
                return True
    return False


def print_map(name: str, matrix: list[list]):
    matrix2 = deepcopy(matrix)
    print(f"----print for {name} BEGIN")
    for h in matrix2:
        y = [str(n) for n in h]
        print(",".join(y))
    print(f"----print for {name} END")


def ec(content: str) -> str:
    referral_content = urllib.parse.quote(content.encode()).encode()
    return base64.b64encode(referral_content).decode("utf-8")


class OrdzSolverLibPo(IOBase):
    """
    the only solver for ordz game play automatically.
    """

    def __init__(self):
        self.matrix: list[list] = []
        self.reference_matrix: list[list] = []
        self.bomb_matrix = []
        self.step_of_maps = []
        self.puzzle_f = ""
        self.puzzle_next_i = 0
        self.puzzle_sizzle_limit = 0
        self.puzzle_drops = []
        self._round = 1

    def reset(self):
        self.matrix: list[list] = []
        self.reference_matrix: list[list] = []
        self.bomb_matrix = []
        self.step_of_maps = []
        self.puzzle_f = ""
        self.puzzle_next_i = 0
        self.puzzle_sizzle_limit = 0
        self.puzzle_drops = []
        self._round = 1

    def external_save_content(self, x: str):
        ...

    def check_success(self, d: dict):
        return True

    def check_key_bool(self, key: str, dictionary: dict, if_true_do_this):
        if key in dictionary:
            do = dictionary[key]
            if isinstance(do, bool):
                if do is True:
                    if_true_do_this()

    def useDemo(self):
        self.reset()
        self.puzzle_f = ""
        self.matrix = DEMO_MAP
        self.reference_matrix = DEMO_MAP
        self.puzzle_drops = self.zlist().split(",")

    def decode_puzzle(self, puzzle: str):
        print("NEW GAME")
        self.reset()
        puzzle_data_decoded = base64.b64decode(puzzle).decode('utf-8')
        self.puzzle_f = puzzle_data_decoded
        arr = json.loads(puzzle_data_decoded)
        self.matrix = deepcopy(arr)
        self.reference_matrix = deepcopy(arr)
        self.puzzle_drops = self.zlist().split(",")

    def compute_explosions_lines_xy(self, start: Tuple[int, int]):
        move_collections = []
        for (mx, my) in POSSIBLE_DIRECTIONS:
            move = [start]
            (x, y) = start
            i, j = x + mx, y + my
            check_res = self.check_xy(start, (i, j))
            if isinstance(check_res, bool) is False:
                (score, matrix) = check_res
                if score > 0:
                    move.append((i, j))
                    move_collections.append({
                        "move": move,
                        "s": score,
                        "m": matrix
                    })

        return move_collections

    def check_xy(self, swap_start: Tuple[int, int], swap_end: Tuple[int, int]) -> Tuple[int, list[list]]:
        evaluate_matrix = deepcopy(self.matrix)
        (x1, y1) = swap_start
        (x2, y2) = swap_end
        if 0 <= x2 < COL_AMOUNT and 0 <= y2 < ROW_AMOUNT:
            # swap
            evaluate_matrix[y1][x1], evaluate_matrix[y2][x2] = evaluate_matrix[y2][x2], evaluate_matrix[y1][x1]
            score = simple_check_explodes(evaluate_matrix)
            return len(score), evaluate_matrix
        else:
            return False

    def one_round(self):
        # while True:
        play_cam = []
        for r in range(COL_AMOUNT):
            j = 0
            while j < ROW_AMOUNT:
                explode_map = self.compute_explosions_lines_xy((r, j))
                if len(explode_map) > 0:
                    play_cam += explode_map
                j += 1
        if len(play_cam) == 0:
            return False
        play_cam = sorted(play_cam, key=lambda x: -x["s"])[0]
        answer_matrix = play_cam["m"]
        print_map("best move", answer_matrix)
        self.step_of_maps.append(deepcopy(answer_matrix))
        return self.next_map(answer_matrix)

    def flow_rounds(self):
        self._round = 1
        while True:
            print(f"PLAY ROUND {self._round}")
            res = self.one_round()
            if isinstance(res, bool) is True:
                break
            self._round += 1
        print("END GAME")
        return self.step_of_maps

    def decode_calculate_t(self, wallet_address: str):
        self.flow_rounds()
        current_time = datetime.datetime.now().timestamp()
        current_time = int(current_time)
        ac = ec(f"{json.dumps(self.step_of_maps)}-b-{self.puzzle_f}-b-{wallet_address}-b-{current_time}")
        b = base36encoderequiredstr()[2:6]
        c = base36encoderequiredstr()[2:10]
        token_t = f"{ac[:5]}{b}{ac[5:12]}{c}{ac[12:]}"
        return token_t

    def next_map(self, check_map: list[list]):
        checked = simple_check_explodes(check_map)
        self.bomb_matrix = check_map
        for (x, y) in checked:
            self.bomb_matrix[x][y] = ORDZ_BOMB
        empty_map = self.fill03()
        print_map("bomb matrix", self.bomb_matrix)
        print_map("fill matrix", empty_map)
        move_down_list = self.fill04()
        before = self.fill05(move_down_list, empty_map)
        print_map("moved down tiles", before)
        self.matrix = deepcopy(before)
        if len(simple_check_explodes(before)) > 0:
            print("double checked and there are more to do...")
            return self.next_map(before)
        else:
            return before

    def zlist(self) -> str:
        if self.puzzle_f == "":
            f = self.reference_matrix
        else:
            f = json.loads(self.puzzle_f)
        return ','.join(str(item) for innerlist in f for item in innerlist)

    def calculate_next_puzzle(self) -> int:
        a = self.puzzle_next_i
        puzzle_sizzles = len(self.puzzle_drops)
        new_i = a % puzzle_sizzles
        n = self.puzzle_drops[new_i]
        self.puzzle_next_i += 1
        return int(n)

    def zero_field(self) -> list[list]:
        drop = []
        for y in range(ROW_AMOUNT):
            row = []
            for y in range(COL_AMOUNT):
                tile = random.choice(["_", "_", "_", "_"])
                row.append(tile)
            drop.append(row)
        return drop

    def fill03(self):
        filled_bomb = deepcopy(self.bomb_matrix)
        empty_map = self.zero_field()
        new_bomb_allocations = []
        for y in range(0, ROW_AMOUNT):
            for x in range(0, COL_AMOUNT):
                if filled_bomb[y][x] == ORDZ_BOMB:
                    new_bomb_allocations.append((y, x))

        need_bombs = len(new_bomb_allocations)

        for (y, x) in new_bomb_allocations:
            empty_map[y][x] = str(self.calculate_next_puzzle())

        return empty_map

    def fill04(self) -> list[Tuple]:
        # position to the fill puzzle on top
        r = ROW_AMOUNT - 1
        pre_row = []
        while r >= 0:
            for j in range(0, COL_AMOUNT):
                sum = 0
                if fill04_checker(j, pre_row) is True:
                    continue
                b = self.bomb_matrix[r][j]
                if b == ORDZ_BOMB:
                    for f in range(ROW_AMOUNT):
                        if self.bomb_matrix[f][j] == ORDZ_BOMB:
                            sum += 1
                    pre_row.append((j, sum, r))
            r -= 1
        return pre_row

    def fill05(self, move_down_list: list[Tuple], empty_map: list[list]):
        final = deepcopy(self.bomb_matrix)
        for col, count, s in move_down_list:
            t = s
            while t >= 0:
                capture = s - count - t
                # self.print_special(3, capture)
                if capture >= 0:
                    final[s - t][col] = self.bomb_matrix[capture][col]
                else:
                    final[s - t][col] = empty_map[s + capture + 1][col]
                t -= 1

        return final

    def print_special(self, n: int, content: str):
        if self._round == n:
            print(content)


class SimpleSolver:
    def __init__(self):
        self.board_size = 9
        self.match_list = [(0, 1, 13, 19), (2, 3, 14, 20), (4, 5, 15, 21), (6, 7, 18, 22), (8, 9, 16, 23),
                           (10, 11, 17, 24)]

        self.special_candies = [1, 3, 5, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        self.simple_candies = [0, 2, 4, 6, 8, 10]
        self.striped_candies_h = [1, 3, 5, 7, 9, 11]
        self.striped_candies_v = range(13, 19)

        self.striped_candies = self.striped_candies_h[:]
        self.striped_candies.extend(self.striped_candies_v)

        self.wrapped_candies = range(19, 25)
        self.chocolate = [12]
        self.game_board = None
        self.potential_start_coords = set()

    def get_score(self, candy_type):
        if candy_type in self.simple_candies:
            return 20
        if candy_type in self.striped_candies:
            return 120
        if candy_type in self.wrapped_candies:
            return 300

        return 0

    def compute_score(self, board, candies_coords):
        score = 0
        for coords in candies_coords:
            candy_value = board[coords[0]][coords[1]]
            score += self.get_score(candy_value)

        if len(candies_coords) == 4:
            score *= 3
        if len(candies_coords) >= 5:
            score *= 10
        return score

    def compute_explosions_chocolate(self, board, color):
        to_explode = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.candy_matches(board[i][j], color):
                    to_explode.append((i, j))

        return to_explode

    def get_striped_explosion(self, board, coords):
        to_explode = []
        candy_type = board[coords[0]][coords[1]]
        if candy_type in self.striped_candies_h:
            for k in range(self.board_size):
                to_explode.append((coords[0], k))
        if candy_type in self.striped_candies_v:
            for k in range(self.board_size):
                to_explode.append((k, coords[1]))

        return to_explode

    def candy_matches(self, type1, type2):
        if type1 == type2:
            return True
        else:
            for match in self.match_list:
                if type1 in match and type2 in match:
                    return True

        return False

    def compute_explosions_lines(self, board: list[list], start: Tuple[int, int]):
        directions = [[(-1, 0), (1, 0)],  # vertical
                      [(0, -1), (0, 1)]]  # horizontal
        to_explode = []
        for dirs in directions:
            open_list = [start]
            for d in dirs:
                i = start[0] + d[0]
                j = start[1] + d[1]
                while 0 <= i < self.board_size and 0 <= j < self.board_size and board[i][j] != -1 \
                        and self.candy_matches(board[i][j], board[start[0]][start[1]]):
                    open_list.append((i, j))
                    i += d[0]
                    j += d[1]

            if len(open_list) >= 3:
                for element in open_list:
                    if element not in to_explode:
                        if board[element[0]][element[1]] in self.striped_candies:
                            to_explode.extend(self.get_striped_explosion(board, element))
                        else:
                            to_explode.append(element)

        return to_explode

    def compute_explosions(self, start, end, board):
        chocolate_multiplier = 1
        to_explode = []

        if board[start[0]][start[1]] in self.special_candies and board[end[0]][end[1]] in self.special_candies:
            score = 500000
            to_explode = [start, end]
        else:
            if board[start[0]][start[1]] == 12:  # chocolate
                to_explode = self.compute_explosions_chocolate(board, board[end[0]][end[1]])
                chocolate_multiplier = 100
            else:
                to_explode = self.compute_explosions_lines(board, start)

            to_explode.sort(key=(lambda x: x[0]))
            score = self.compute_score(board, to_explode) * chocolate_multiplier

        if len(to_explode) == 4 and board[start[0]][start[1]] != 12:  # striped candy
            board[start[0]][start[1]] += 1
            to_explode.remove(start)

        # if len(to_explode) > 0:
        #    print '\n\nStarting board:'
        #    dbg.print_board(board)

        # Slide the other candies down after explosions take place
        for coord in to_explode:
            i, j = coord

            while i > 0:
                if board[i - 1][j] != -1 and (i - 1, j) not in self.potential_start_coords:
                    self.potential_start_coords.add((i, j))
                board[i][j], board[i - 1][j] = board[i - 1][j], board[i][j]
                i -= 1
            board[i][j] = -1

        # if len(to_explode) > 0:
        # print '\nResult from {0}, count={1}, score={2}:'.format(start, len(to_explode), score)
        # dbg.print_board(board)

        return score, board

    def evaluate_board(self, start, end, board):
        total_score, new_board = self.compute_explosions(start, end, board)
        score = total_score
        multiplier = 1
        while score > 0:
            use_new = False
            if use_new:
                potential_start = deepcopy(self.potential_start_coords)
                self.potential_start_coords = set()
                score = 0
                for coord in potential_start:
                    score, new_board = self.compute_explosions((coord[0], coord[1]), end, new_board)
                    if score > 0:
                        total_score += score + multiplier * 60
                        multiplier += 2
            else:
                for i in range(0, self.board_size):
                    for j in range(0, self.board_size):
                        score, new_board = self.compute_explosions((i, j), end, new_board)
                        if score > 0:
                            total_score += score + multiplier * 60
                            multiplier += 2

        return total_score, new_board

    def check_direction(self, start, dir):
        end = (start[0] + dir[0], start[1] + dir[1])
        board = deepcopy(self.game_board)
        if start[0] < 0 or start[0] > self.board_size or end[0] < 0 or end[0] > self.board_size \
                or start[1] < 0 or start[1] > self.board_size or end[1] < 0 or end[1] > self.board_size:
            return -1, [], None

        # swap
        board[start[0]][start[1]], board[end[0]][end[1]] = board[end[0]][end[1]], board[start[0]][start[1]]
        score_start, start_board = self.evaluate_board(start, end, board)
        score_end, end_board = self.evaluate_board(end, start, board)

        if score_start > score_end:
            return score_start, [start, end], start_board
        else:
            return score_end, [end, start], end_board

    def solve_board(self, board):
        self.game_board = board
        max_score = 0
        chosen_move = []
        for i in range(0, 8):
            for j in range(0, 8):
                possible_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                for d in possible_directions:
                    score, move, b = self.check_direction((i, j), d)
                    if score >= max_score:
                        max_score = score
                        chosen_move = move

        return max_score, chosen_move
