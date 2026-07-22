from src.utils.db_logger import DBLogger
from src.utils.config_loader import load_config
import random
from datetime import datetime, timedelta, timezone

cfg = load_config('config/default.yaml')
db = DBLogger(cfg['logging']['db_path'])
base = datetime.now(timezone.utc) - timedelta(minutes=20)

for i in range(15):
    ts = (base + timedelta(minutes=i)).isoformat()
    cls = random.choice(['fire', 'smoke'])
    conf = round(random.uniform(0.3, 0.95), 2)
    alert = conf >= 0.6 and random.random() > 0.4
    db.log_detection(cls, conf, bbox=[10, 10, 50, 50], alert_triggered=alert, timestamp=ts)

print(db.get_stats())