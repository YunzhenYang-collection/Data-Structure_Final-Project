import json
import os
from datetime import datetime

REMINDER_PATH = 'reminders.json'

def _load_all():
    if not os.path.exists(REMINDER_PATH):
        return []
    with open(REMINDER_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_all(reminders):
    with open(REMINDER_PATH, 'w', encoding='utf-8') as f:
        json.dump(reminders, f, ensure_ascii=False)

def get_all_reminders():
    return _load_all()

def add_reminder(content, date):
    reminders = _load_all()
    rid = int(datetime.now().timestamp() * 1000)
    new_reminder = {'rid': rid, 'content': content, 'date': date}
    reminders.append(new_reminder)
    _save_all(reminders)
    return new_reminder

def delete_reminder(rid):
    reminders = _load_all()
    reminders = [r for r in reminders if str(r['rid']) != str(rid)]
    _save_all(reminders)
    return True
