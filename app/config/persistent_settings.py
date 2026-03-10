from app.database.models import AppSetting


def get_setting(key, default=None):

    from app.database.db import SessionLocal

    db = SessionLocal()

    try:

        setting = db.query(AppSetting).filter(AppSetting.key == key).first()

        if setting:
            return setting.value

        return default

    finally:
        db.close()


def set_setting(key, value):

    from app.database.db import SessionLocal

    db = SessionLocal()

    try:

        setting = db.query(AppSetting).filter(AppSetting.key == key).first()

        if setting:
            setting.value = value
        else:
            setting = AppSetting(key=key, value=value)
            db.add(setting)

        db.commit()

    finally:
        db.close()