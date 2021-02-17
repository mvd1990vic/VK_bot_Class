#!/usr/local/bin/python
from pony.orm import Database, Required, Json

from settings import DB_CONFIG


db = Database()
db.bind(**DB_CONFIG)

class UserState(db.Entity):
    """Состояние пользователя внутри сценария"""
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)

db.generate_mapping(create_tables=True)