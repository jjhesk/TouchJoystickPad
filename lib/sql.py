# !/usr/bin/env python
# coding: utf-8
import datetime
import sqlite3
import uuid
from typing import Tuple

from lib.const import DATAPATH_BASE
from SQLiteAsJSON import ManageDB
from SQLiteAsJSON.SQLiteAsJSON import db_logger
import os.path
import json
import random
from requests import Response

from dateutil.parser import parse


class SqlDataNotFound(Exception):
    pass


def obj_to_tuple(obj) -> Tuple[str, str]:
    keys = ''
    values = ''
    for key, value in obj.items():
        keys = f'{keys},{key}' if keys != '' else key
        values = f'{values}, :{key}' if values != '' else f':{key}'

    return keys, values


def obj_to_string(update_config) -> str:
    update_string = ''
    index = 0
    for key, value in update_config.items():
        update_string = update_string + f"{key}='{value}'," if index < len(
            update_config) - 1 else update_string + f"{key}='{value}'"
        index = index + 1

    return update_string


class CompanyUserBase(ManageDB):
    """
    modified blockchain db controller
    """

    def found_table(self, tableName: str) -> bool:
        sqlStatement = f"SELECT name FROM sqlite_sequence WHERE type='table' AND name='{tableName}'"
        cursor = self.conn.cursor()
        cursor.execute(sqlStatement)
        db_result = cursor.fetchone()
        if db_result is None:
            return False
        else:
            return True

    def has_address(self, tbl: str, address_key: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {tbl} WHERE address = ?", (address_key,))
        db_result = cursor.fetchone()
        cursor.close()
        if db_result is None:
            return False
        else:
            return True

    def has_row(self, tbl: str, member_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {tbl} WHERE member_id = ?", (member_id,))
        db_result = cursor.fetchone()
        cursor.close()
        if db_result is None:
            return False
        else:
            return True

    def update_by_id(self, tbl: str, address_key: str, params: dict) -> bool:
        if self.has_address(tbl, address_key) is False:
            return False
        if address_key[0:2] == "bc":
            try:
                columns = obj_to_string(params)
                # update query
                self.conn.execute(f"UPDATE {tbl} set {columns} where address='{address_key}'")
            except Exception as E:
                db_logger.error('Data Update Error : ', E)
                return False

            self.conn.commit()
            return True
        else:
            return False

    def insert_row_dat(self, tbl: str, params: dict, need_member_uuid: bool = True) -> bool:
        if need_member_uuid:
            # Create UUID
            params.update({
                "member_id": uuid.uuid4().hex
            })
        # params["timestamp"] = round(time.time() * 1000)  # Current unix time in milliseconds
        (k, v) = obj_to_tuple(params)
        # insert query
        try:
            query = (
                f'INSERT INTO {tbl} ({k}) VALUES ({v})'
            )
            self.conn.execute(query, params)
            self.conn.commit()
        except (
                sqlite3.OperationalError,
                Exception
        ) as e:
            db_logger.error('Data Insert Error : ', e)
            return False
        return True

    def insert_row_t2(self, tbl: str, params: dict) -> bool:
        (k, v) = obj_to_tuple(params)
        try:
            query = (
                f'INSERT INTO {tbl} ({k}) VALUES ({v})'
            )
            self.conn.execute(query, params)
            self.conn.commit()
        except (
                sqlite3.OperationalError,
                Exception
        ) as e:
            db_logger.error('Data Insert Error : ', e)
            return False
        return True

    def get_member_res(self, tbl: str, address_key: str) -> dict:
        cursor = self.conn.cursor()
        _da = {}
        member = ''
        try:
            cursor.execute(f'SELECT member_id, res FROM {tbl} WHERE address = ?',
                           (address_key,))
            (member, res_01,) = cursor.fetchone()
            _da = json.loads(res_01)

        except TypeError as c:
            raise SqlDataNotFound()
        except Exception as E:
            db_logger.error('NOT FOUND.. : ', E)
            raise SqlDataNotFound()

        return _da

    def get_next_action(self, tbl: str, address_key: str) -> dict:
        cursor = self.conn.cursor()
        _da = {}
        next_action = None
        try:
            cursor.execute(f'SELECT member_id, next_action FROM {tbl} WHERE address = ?',
                           (address_key,))
            (tx_id, next_action) = cursor.fetchone()
        except Exception as E:
            db_logger.error('Data Insert Error : ', E)
            raise SqlDataNotFound()

        _da = json.loads(next_action)
        return _da

    def get_fight_history_by_address(self, tbl: str, address_loc: str) -> list:
        cursor = self.conn.cursor()
        times = []
        try:
            cursor.execute(f'SELECT create_tme, end_tme FROM {tbl} WHERE address = ?',
                           (address_loc,))
            times = cursor.fetchall()
        except TypeError as v:
            db_logger.error('Key data error: ', v)
            raise SqlDataNotFound()
        except Exception as e:
            db_logger.error('Query data error: ', e)
            raise SqlDataNotFound()
        return times

    def get_raw_json_profile(self, tbl: str, address_key: str) -> dict:
        cursor = self.conn.cursor()
        _da = {}
        profile = None
        try:
            cursor.execute(f'SELECT address, profile FROM {tbl} WHERE address = ?',
                           (address_key,))
            (tx_id, profile) = cursor.fetchone()
        except TypeError as v:
            db_logger.error('Key data error: ', v)
            raise SqlDataNotFound()
        except Exception as e:
            db_logger.error('Query data error: ', e)
            raise SqlDataNotFound()
        _da = json.loads(profile)
        return _da

    def get_raw_json_last_scene(self, tbl: str, address_key: str) -> dict:
        cursor = self.conn.cursor()
        _da = {}
        profile = None
        try:
            cursor.execute(f'SELECT address, last_fight FROM {tbl} WHERE address = ?',
                           (address_key,))
            (tx_id, profile) = cursor.fetchone()
        except Exception as E:
            db_logger.error('Data Insert Error : ', E)
            raise SqlDataNotFound()
        _da = json.loads(profile)
        return _da

    def _is_what_ready_res(self, tble_member: str, address: str, key: str) -> bool:
        # if self.has_address(tble_member, address) is False:
        #    return False

        current_time = datetime.datetime.now().timestamp()
        current_time = int(current_time)
        from_dat = self.get_next_action(tble_member, address)
        if key in from_dat:
            time_next = from_dat[key]
            return current_time > time_next

        print(f"key {key} not exist. decision is OK.")
        return True

    def _check_point_update_res(self, tble_member: str, address: str, key: str, next_seconds: int = 3600):
        from_dat = self.get_next_action(tble_member, address)
        current_time = datetime.datetime.now().timestamp()
        current_time = int(current_time)
        from_dat.update({
            key: current_time + next_seconds
        })
        self.update_by_id(tble_member, address, {
            "next_action": json.dumps(from_dat)
        })

    def get_first_row(self, tbl: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT member_id FROM {tbl}")
        (member_id,) = cursor.fetchone()
        cursor.close()
        return member_id

    def get_child_code(self, tbl: str, atId: int) -> str:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT member_id, referral_code FROM {tbl} where member_id = ?", (atId,))
        (member_id, refrral_code) = cursor.fetchone()
        cursor.close()
        return refrral_code

    def user_history(self, ):
        cursor = self.conn.cursor()
        cursor.execute(f"address")
        cursor.fetchall()

    def keepcopy(self, file_path: str, r: Response):
        try:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        except FileNotFoundError:
            with open(file_path, 'a+') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)


class TrackerKeep(CompanyUserBase):
    def __init__(self):
        self._tblembr = "ordz_account"
        self._tblestats = "ordz_stats"
        self._tblehistory = "ordz_fight_history"
        path_db = os.path.join(DATAPATH_BASE, 'cache.db')
        schema = os.path.join(DATAPATH_BASE, 'schema.json')
        self.cache_db_path = path_db
        new_db = False if os.path.isfile(path_db) else True
        super().__init__(
            db_name=path_db,
            db_config_file_path=schema,
            same_thread=False
        )
        if new_db:
            self.create_table()
        self.user_addr = ""

    def _check_point_update(self, key: str, how_long_seconds: int = 3600):
        self._check_point_update_res(self._tblembr, self.user_addr, key, how_long_seconds)

    def _is_what_ready(self, key: str) -> bool:
        return self._is_what_ready_res(self._tblembr, self.user_addr, key)

    def check_shop_management_ready(self) -> bool:
        return self._is_what_ready("shop_management")

    def check_shop_visit(self):
        self._check_point_update("shop_management")

    def check_token_claim_ready(self) -> bool:
        return self._is_what_ready("token_claim")

    def check_point_token_claim(self, msecond: int):
        self._check_point_update("token_claim", msecond)

    def check_point_daily_ops_ready(self) -> bool:
        return self._is_what_ready("daily_operation")

    def check_point_daily_ops(self):
        self._check_point_update("daily_operation", 3600 * 24)

    def insert_new(self, update_params: dict) -> bool:
        return self.insert_row_dat(self._tblembr, update_params)

    def update_param(self, address: str, update_param: dict) -> bool:
        return self.update_by_id(self._tblembr, address, update_param)

    def has_the_address(self, address: str) -> bool:
        return self.has_address(self._tblembr, address)

    def update_res(self, address: str, res_file: dict):
        update_dic = {
            "res": json.dumps(res_file)
        }
        return self.update_param(address, update_dic)

    def use_insert_user_dat(self, address: str, _pk: str, referralcode_: str, parentcode_: str,
                            file: dict) -> bool:
        p = {
            "address": address,
            "pk": _pk,
            "parent_code": parentcode_,
            "referral_code": referralcode_,
            "next_action": "{}",
            "res": json.dumps(file)
        }
        return self.insert_new(p)

    def total_count(self, tbl: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as count FROM {tbl}")
        (count,) = cursor.fetchone()
        cursor.close()
        if count > 0:
            print(count)
        return count

    def set_address(self, address_vibe: str):
        if address_vibe != self.user_addr:
            self.user_addr = address_vibe

    def get_ordz_coin(self) -> int:
        da = self.get_member_res(self._tblembr, self.user_addr)
        if "deposit_number" in da:
            return int(da["deposit_number"])
        return 0

    def is_twitter_account_bind(self) -> bool:
        da = self.get_member_res(self._tblembr, self.user_addr)
        print(da)
        if "twitter_id" in da:
            twitter_id = da["twitter_id"]
            print(f"twitter account ID is found {twitter_id}")
            if twitter_id is None or twitter_id == "":
                return False
            else:
                return True
        return False

    def tipping_point(self, pk: str, res: dict):
        # first time to receive profile data to the account.
        if self.has_the_address(self.user_addr) is False:
            self.use_insert_user_dat(self.user_addr, pk, "", "", res)
        else:
            self.update_res(self.user_addr, res)

    def traits(self, res: dict):
        if self.has_address(self._tblestats, self.user_addr) is False:
            self.insert_row_t2(self._tblestats, {
                "address": self.user_addr,
                "traits": json.dumps(res),
                "heroes": json.dumps({}),
                "profile": json.dumps({}),
                "last_fight": json.dumps({}),
            })
        else:
            self.update_by_id(self._tblestats, self.user_addr, {
                "traits": json.dumps(res),
            })

    def get_fight_meta(self, book: str = None):
        t = self.get_raw_json_last_scene(self._tblestats, self.user_addr)
        if book is None:
            return t
        else:
            if book not in t:
                raise SqlDataNotFound()
            book_result = t[book]
            return book_result

    def get_profile_hero_tokens(self, count: int = 1) -> list:
        if self.has_address(self._tblestats, self.user_addr) is False:
            return []

        f = self.get_raw_json_profile(self._tblestats, self.user_addr)
        if "hero_tokens" in f:
            fd = f["hero_tokens"]
            if len(fd) > 0:
                return f["hero_tokens"][:count]

        raise SqlDataNotFound()

    def get_session_tokens(self) -> str:
        try:
            f = self.get_member_res(self._tblembr, self.user_addr)
            if "session" in f:
                fd = f["session"]
                return fd
            else:
                return ""
        except SqlDataNotFound:
            return ""

    def get_detail_token(self):
        return self._read_key_of_what("battle_detail.detail_token")

    def get_activity_token(self) -> str:
        return self._read_key_of_what("fight_scene.activity_token")

    def get_puzzle(self) -> str:
        return self.get_fight_meta("b64_puzzle")

    def get_claim_token(self) -> str:
        return self.get_fight_meta("claim_token")

    def any_heroes_alive(self) -> bool:
        battle_detail = self.get_fight_meta("battle_detail")
        op_hp = battle_detail["opponent_remaining_hp"] if "opponent_remaining_hp" in battle_detail else 0
        my_hp = battle_detail["hero_remaining_hp"] if "hero_remaining_hp" in battle_detail else 0
        return my_hp > 0 and op_hp > 0

    def _read_key_of_what(self, long_key: str):
        parts = long_key.split(".")
        battle_detail = self.get_fight_meta(parts[0])
        if parts[1] in battle_detail:
            return battle_detail[parts[1]]
        else:
            print(f"no {parts[1]} is found.")
            return ""

    def update_map_hash(self, hash: str):
        self._update_last_fight_of_what("b64_puzzle", hash)

    def update_solve_hash(self, hash: str):
        self._update_last_fight_of_what("b64_solution", hash)

    def update_detail_token(self, hash: str):
        self._update_last_fight_of_what("detail_token", hash)

    def update_in_game_token(self, hash: str):
        self._update_last_fight_of_what("claim_token", hash)

    def update_fight_scene(self, res: dict):
        self._update_last_fight_of_what("fight_scene", res)

    def update_last_battle(self, res: dict):
        self._update_last_fight_of_what("battle_detail", res)

    def _update_last_fight_of_what(self, key: str, res: any):
        t = self.get_fight_meta()
        t.update({key: res})
        self.update_by_id(self._tblestats, self.user_addr, {
            "last_fight": json.dumps(t)
        })

    def profile_update(self, key: str, res):
        f = self.get_raw_json_profile(self._tblestats, self.user_addr)
        f.update({key: res})
        self.update_by_id(self._tblestats, self.user_addr, {
            "profile": json.dumps(f),
        })

    def has_the_history(self, t1: int, t2: int):
        cursor = self.conn.cursor()
        db_result = None
        try:
            cursor.execute(f'SELECT * FROM {self._tblehistory} WHERE create_tme = ? AND end_tme = ?',
                           (t1, t2,))
            db_result = cursor.fetchone()
        except TypeError as v:
            db_logger.error('Key data error: ', v)
            raise SqlDataNotFound()
        except Exception as e:
            db_logger.error('Query data error: ', e)
            raise SqlDataNotFound()
        if db_result is None:
            return False
        else:
            return True

    def sync_history(self, data_history_list: list):
        for data in data_history_list:
            t1 = int(parse(data["created_at"]).timestamp().real)
            t2 = int(parse(data["end_at"]).timestamp().real)
            if self.has_the_history(t1, t2):
                continue

            d = {
                "address": "" if data["address"] is None else data["address"],
                "opponent_address": "NA" if data["opponent_address"] is None else data["opponent_address"],
                "create_tme": t1,
                "end_tme": t2,
                "ordz_box": int(data["pk_ordz"]),
                "data": json.dumps({
                    "battle_multiple": data["battle_multiple"],
                    "rank_result": data["rank_result"],
                    "reward_result": data["reward_result"],
                    "traits": data["traits"],
                    "chest_data": data["chest_data"],
                    "blitz": data["blitz"],
                    "blitz_total_times": data["blitz_total_times"],
                    "immune": data["immune"],
                })
            }

            if self.insert_row_dat(self._tblehistory, d, False) is False:
                print("Error from insert data history", data)

    def is_history_play_confirmed_ready(self) -> bool:
        try:
            f = self.get_fight_history_by_address(self._tblehistory, self.user_addr)
            print(f)
            if len(f) == 0:
                return True

                # 2024-02-14T04:21:38.728000Z
            end_time = sorted([b for (a, b) in f], key=lambda x: -x)[0]
            current_time = datetime.datetime.now().timestamp()
            current_time = int(current_time)
            if current_time - end_time > 24 * 3600:
                return True

        except Exception:
            return True

    def isFreePlayLimitReached(self) -> bool:
        try:
            if self.has_address(self._tblestats, self.user_addr) is False:
                return False

            f = self.get_raw_json_profile(self._tblestats, self.user_addr)
            if "today" in f:
                fd = f["today"]
                total_free_play = fd["training_free_total_times"]
                current_free_play = fd["training_free_activity_times"]
                if total_free_play - current_free_play <= 0:
                    return True
            return False
        except SqlDataNotFound:
            return False
        except Exception:
            return False

    def heroes(self, res: dict):
        self.update_by_id(self._tblestats, self.user_addr, {
            "heroes": json.dumps(res)
        })

    def get_random_historic_parent_code(self) -> str:
        """
        the goal is to get the random child referral code from the existing table members
        :return:
        """
        try:
            count_members = self.total_count(self._tblembr)
            if count_members > 10:
                random_number = random.randint(1, count_members)
            else:
                first_id = self.get_first_row(self._tblembr)
                print(f"only use the first row ID", first_id)
                return self.get_child_code(self._tblembr, first_id)
            print(f"check number {random_number}")
            if self.has_row(self._tblembr, random_number) is True:
                return self.get_child_code(self._tblembr, random_number)
            else:
                return self.get_random_historic_parent_code()

        except RecursionError:
            first_id = self.get_first_row(self._tblembr)
            print(f"only use the first row ID", first_id)
            return self.get_child_code(self._tblembr, first_id)
