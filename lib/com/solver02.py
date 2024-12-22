# !/usr/bin/env python
# coding: utf-8
import base64
import datetime
import json
import random
import time
import urllib.parse
from typing import Tuple, Union
from lib.com.iobase import IOBase
from lib.const import MemoryErr

ROW_AMOUNT = 6
COL_AMOUNT = 8
MAX_SCORE = 40
ORDZ_BOMB = "■"
POSSIBLE_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DEMO_MAP = [[3, 1, 2, 0, 3, 1, 2, 4],
            [1, 3, 4, 1, 1, 2, 3, 2],
            [4, 2, 0, 3, 0, 1, 3, 0],
            [4, 1, 3, 0, 3, 3, 2, 1],
            [1, 3, 1, 3, 3, 4, 3, 0],
            [2, 3, 0, 1, 0, 4, 0, 4]]


def copy_dereference(any):
    return json.loads(json.dumps(any))


def base36encode(number):
    if not isinstance(number, (int, float)):
        raise TypeError('number must be an integer')
    is_negative = number < 0
    number = abs(number)

    alphabet, base36 = ['0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', '']

    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    if is_negative:
        base36 = '-' + base36

    return base36 or alphabet[0]


def base36_encode_rand() -> str:
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    generated_characters = ''.join(random.choice(alphabet) for _ in range(10))
    return f"1.{generated_characters}"


def b36_encode(i):
    if i < 0: return "-" + b36_encode(-i)
    if i < 36: return "0123456789abcdefghijklmnopqrstuvwxyz"[i]
    return b36_encode(i // 36) + b36_encode(i % 36)


def base36_encode_rand() -> str:
    f = random.randrange(100000000999000000, 900000000000000999)
    value = b36_encode(f)
    return value


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

    for c in range(COL_AMOUNT):
        i = 0
        j = 1
        while j < ROW_AMOUNT:
            # print(c, i, j)
            if map_matrix[i][c] != map_matrix[j][c]:
                if j - i >= 3:
                    for m in range(i, j):
                        if (m, c) in results:
                            print("FOUND THE SAME SPOT.... SKIP")
                            continue
                        results.append((m, c))
                i = j
            j += 1
    # results = list(set(results))
    # results = sorted(results, key=lambda a: a)
    # print(results)
    # if len(results)>0:
    #    print(results)
    return results


def print_map(name: str, matrix: list[list]):
    print(f"----print for {name} BEGIN")
    for h in matrix:
        y = [str(n) for n in h]
        print(",".join(y))
    print(f"----print for {name} END")


def print_map_double(name: str, matrix1: list[list], matrix2: list[list]):
    matrix_a = copy_dereference(matrix1)
    matrix_b = copy_dereference(matrix2)
    line_1 = []
    line_2 = []
    for h in matrix_a:
        y = [str(n) for n in h]
        line_1.append(",".join(y))
    for h in matrix_b:
        y = [str(n) for n in h]
        line_2.append(",".join(y))
    print(f"----print for {name} BEGIN")
    for t in range(len(line_1)):
        print(f"{line_1[t]}  {line_2[t]}")
    print(f"----print for {name} END")


def print_map_difference(label: str, m1, m2):
    matrix_a = copy_dereference(m1)
    matrix_b = copy_dereference(m2)
    for y in range(0, ROW_AMOUNT):
        for x in range(0, COL_AMOUNT):
            if matrix_a[y][x] != matrix_b[y][x]:
                matrix_a[y][x] = f"[{matrix_a[y][x]}]"
                matrix_b[y][x] = f"[{matrix_b[y][x]}]"
            else:
                matrix_a[y][x] = f" {matrix_a[y][x]} "
                matrix_b[y][x] = f" {matrix_b[y][x]} "
    print_map_double(label, matrix_a, matrix_b)


def ec(content: str) -> str:
    referral_content = urllib.parse.quote(content.encode()).encode()
    return base64.b64encode(referral_content).decode("utf-8")


def drop_map(from_bomb_map: list[list]):
    drop_num = []
    r = ROW_AMOUNT - 1
    while r >= 0:
        for j in range(0, COL_AMOUNT):
            sum = 0
            _row = r + 1
            while _row < ROW_AMOUNT:
                if from_bomb_map[_row][j] == ORDZ_BOMB:
                    sum += 1
                _row += 1
            drop_num.append((r, j, sum))
            if sum > 0:
                from_bomb_map[r + sum][j] = from_bomb_map[r][j]
                from_bomb_map[r][j] = ORDZ_BOMB

        r -= 1
    return from_bomb_map, drop_num


def line_checker_score(check_map: list[list], swap_start: Tuple[int, int], swap_end: Tuple[int, int]) -> Tuple[
    int, list[list]]:
    evaluate_matrix = copy_dereference(check_map)
    (x1, y1) = swap_start
    (x2, y2) = swap_end
    if 0 <= x2 < COL_AMOUNT and 0 <= y2 < ROW_AMOUNT:
        # swap
        evaluate_matrix[y1][x1], evaluate_matrix[y2][x2] = evaluate_matrix[y2][x2], evaluate_matrix[y1][x1]
        score = simple_check_explodes(evaluate_matrix)
        return len(score), evaluate_matrix
    else:
        return False


def deepcopy2(f: list[list]):
    return json.loads(json.dumps(f))


def compute_explosions_lines_xy(check: list[list], start: Tuple[int, int]):
    move_collections = []
    for (mx, my) in POSSIBLE_DIRECTIONS:
        move = [start]
        (x, y) = start
        i, j = x + mx, y + my
        check_res = line_checker_score(check, start, (i, j))
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


class OrdzSolverLib(IOBase):
    """
    the only solver for ordz game play automatically.
    """
    matrix: list[list]
    reference_matrix: list[list]
    _p_matrix: list
    step_of_maps: list
    puzzle_f: str
    puzzle_next_i: int
    puzzle_sizzle_limit: int
    puzzle_drops: list
    _round: int

    def __init__(self):
        self.reset()

    def reset(self):
        self.matrix: list[list] = []
        self.reference_matrix: list[list] = []
        self._p_matrix = []
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

    def decode_remain_hp(self, d: dict):
        hero_remaining_hp = 0
        opponent_remaining_hp = 0

        if "hero_remaining_hp" in d:
            hero_remaining_hp = d["hero_remaining_hp"]
        if "opponent_remaining_hp" in d:
            opponent_remaining_hp = d["opponent_remaining_hp"]

        if opponent_remaining_hp > 0 or hero_remaining_hp > 0:
            print(f"hero: {hero_remaining_hp} , Op: {opponent_remaining_hp}")

        if "pk_ordz" in d:
            pk_ordz = d["pk_ordz"]
            print(f"ORDZ claimed: {pk_ordz}")

    def decode_hero_low_hp(self, d: dict):
        hero_remaining_hp = d["hero_remaining_hp"] if "hero_remaining_hp" in d else 0
        return hero_remaining_hp < 1000

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

    def decode_puzzle(self, puzzle_content: str):
        self.reset()
        print("NEW GAME====")
        puzzle_data_decoded = base64.b64decode(puzzle_content).decode('utf-8')
        self.puzzle_f = puzzle_data_decoded
        self.matrix = json.loads(puzzle_data_decoded)
        self.reference_matrix = json.loads(puzzle_data_decoded)
        self.puzzle_drops = self.zlist().split(",")
        print(puzzle_content)
        print(",".join(self.zlist().split(",")))
        print("============")
        self.flow_rounds()

    def gen_new_map(self):
        puzzle_data_decoded = self.puzzle_f
        arr = json.loads(puzzle_data_decoded)
        random.shuffle(arr)
        self.matrix = copy_dereference(arr)
        self.reference_matrix = copy_dereference(arr)
        self.puzzle_f = json.dumps(arr)
        self.puzzle_drops = self.zlist().split(",")
        print("============generated new puzzle")
        new_puzzle_data = base64.b64encode(json.dumps(arr).encode()).decode('utf-8')
        print(new_puzzle_data)
        print(",".join(self.zlist().split(",")))
        print("============")
        self.flow_rounds()

    def single_op(self):
        # while True:
        play_cam = []
        for r in range(COL_AMOUNT):
            j = 0
            while j < ROW_AMOUNT:
                explode_map = compute_explosions_lines_xy(self.matrix, (r, j))
                if len(explode_map) > 0:
                    play_cam += explode_map
                j += 1
        if len(play_cam) == 0:
            return False
        play_cam = sorted(play_cam, key=lambda x: -x["s"])[0]
        answer_matrix = play_cam["m"]
        # print_map("best move", answer_matrix)
        return self.next_map(answer_matrix)

    def calculate_rounds(self) -> int:
        # find out how many rounds until the 40 max
        print(f"Calculated rounds to be {self._round}")
        return self._round

    def flow_rounds(self):
        self._round = 1
        score = 0
        while True:
            print(f"PLAY ROUND {self._round}")
            res = self.single_op()
            if isinstance(res, bool) is True:
                break
            score = sum([len(y["c"]) for y in self.step_of_maps])
            if score >= MAX_SCORE:
                break
            self._round += 1
        print(f"END GAME @{self._round} with SCORE {score}")

    def decode_calculate_t(self, wallet_address: str):
        if len(self.step_of_maps) <= 3:
            raise MemoryErr()

        current_time = datetime.datetime.now().timestamp()
        current_time = int(current_time) * 1000 + random.randrange(1, 1000)
        self.step_of_maps[len(self.step_of_maps) - 1].pop("e")
        step_tight = json.dumps(self.step_of_maps).replace(" ", "")
        dex = f"{step_tight}-b-{self.puzzle_f}-b-{wallet_address}-b-{current_time}"
        ac = ec(dex)
        b = base36_encode_rand()[3:7]
        c = base36_encode_rand()[3:11]
        f = f"{ac[:5]}{b}{ac[5:12]}{c}{ac[12:]}"
        print("===================== T1")
        # print(b, c)
        # print(dex)
        token_t = f
        # if f[len(f) - 1] == "=":
        # print("1. has padding at the end")
        # token_t = f.replace("=", "")
        # print("2. removed all padding =")
        print("x. ending result..")
        print(token_t[len(token_t) - 50:])
        self.step_of_maps = []
        return f

    def decode_check_validation(self, f: str):
        if f[len(f) - 1] != "=":
            print("1. no padding at the end")
        print("2. ending result..")
        print(f[len(f) - 50:])

    def decode_reverse(self, f: str):
        print("============== DEBUG CHECKING FOR VALIDATION")
        if f[len(f) - 1] != "=":
            print("no padding at the end")
            f = f"{f}="
        A = 4
        B = 8
        w1 = f[:5]
        w4 = f[5:9]
        w8 = f[16:24]
        w9 = f[5 + A:]
        w2 = w9[:7]
        w3 = w9[7 + B:]
        # print(w2)
        content1 = f"{w1}{w2}{w3}"
        content2 = f.replace(w4, "").replace(w8, "")
        assert content1 == content2
        print("============== T1")
        print(w4, w8)
        print("============== T2")
        # print(content1)
        content = base64.b64decode(content2).decode()
        # print(content)
        content = urllib.parse.unquote(content)
        # print(content)
        g = content.split("-b-")

        # print("=====================")
        for t in range(len(g)):
            print(f"============== F{t}")
            print(g[t])
        print("=====TEST DIFFERENCE g[0]vs g[1]")
        print_map_difference("g[1] vs g[0].b", json.loads(g[1]), json.loads(g[0])[0]["b"])
        print("=====TEST SERIAL")
        fex = json.loads(g[1])
        f_li = ','.join(str(item) for innerlist in fex for item in innerlist)
        L2 = [[ji["b"] for ji in j["d"]] for j in json.loads(g[0])]
        f_li2 = ','.join(str(r) for li in L2 for r in li)
        print(L2)
        print(f_li)
        print(f_li2)
        print(f"score = {len(f_li2.split(','))}")
        print("check for each item")
        p = 0
        old_j = None
        for j in json.loads(g[0]):
            if "e" in j:
                if old_j is not None:
                    print_map_difference(f"check step [{p}]", old_j["e"], j["b"])
                old_j = j
                bomb_layout = [(r["a"], r["b"]) for r in j["c"]]
                filled_layout = [(r["a"], r["b"]) for r in j["d"]]
                print("bomb layout", bomb_layout)
                print("fill layout", filled_layout)
                filled_layout_c = j["e"]
                print_map_difference("-b vs -e check", j["b"], filled_layout_c)
                for (pi, i) in filled_layout:
                    y = int(pi.split(",")[0])
                    x = int(pi.split(",")[1])
                    print(y, x, filled_layout_c[y][x], i)
                    assert filled_layout_c[y][x] == int(i)
            else:
                print(f"============== VALID CHECK")
                print(f"e is not found in here round {p}")
                assert p == len(json.loads(g[0])) - 1
            p += 1

    def supplement_map(self, continue_map: list[list]):
        d_map = []
        for y in range(0, ROW_AMOUNT):
            for x in range(0, COL_AMOUNT):
                if continue_map[y][x] == ORDZ_BOMB:
                    new_puzzle = self.calculate_next_puzzle()
                    continue_map[y][x] = new_puzzle
                    d_map.append({
                        "a": f"{y},{x}",
                        "b": new_puzzle
                    })
        return continue_map, d_map

    def bomb_map(self, check_map: list[list]):
        results = simple_check_explodes(check_map)
        # results = list(set(results))
        checked = sorted(results, key=lambda a: a)
        codec = []
        for (r, c) in checked:
            bomb_need = check_map[r][c]
            codec.append({
                "a": f"{r},{c}",
                "b": bomb_need
            })
            check_map[r][c] = ORDZ_BOMB
        print(codec)
        return check_map, codec

    def next_map(self, map0: list[list]):
        b = copy_dereference(map0)
        (map1, c) = self.bomb_map(map0)
        pmap1 = copy_dereference(map1)
        (map2, dropz) = drop_map(map1)
        pmap2 = copy_dereference(map2)
        (self._p_matrix, d) = self.supplement_map(map2)
        print_map_double("changes", pmap1, pmap2)
        print_map("layout-e", self._p_matrix)
        e = copy_dereference(self._p_matrix)
        bomb_layout = [(r["a"], r["b"]) for r in c]
        filled_layout = [(r["a"], r["b"]) for r in d]
        print("bomb layout", bomb_layout)
        print("fill layout", filled_layout)
        self.matrix = self._p_matrix
        pack = {
            "b": b,
            "c": c,
            "d": d,
            "e": self._p_matrix
        }

        self.step_of_maps.append(pack)

        if len(simple_check_explodes(e)) > 0:
            print("looks like there is a double kills before the next fight...")
            return self.next_map(e)
        else:
            return e

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

    def print_special(self, n: int, content: str):
        if self._round == n:
            print(content)
