import sqlite3
import pickle
import threading

class SQLiteStateStore:
  def __init__(self, model, db_path, default_token=0):
    self.t = threading.local()
    self.db_path = db_path
    self.opendb()
    self.model = model
    self.default_token = default_token
    self.t.conn.execute("CREATE TABLE IF NOT EXISTS states (key TEXT PRIMARY KEY, last_token INTEGER, state BINARY)")
    self.t.conn.commit()

  def opendb(self):
    if hasattr(self.t, 'conn'):
      return
    self.t.conn = sqlite3.connect(self.db_path)

  def forward(self, request):
    self.opendb()
    key = request.key
    r = self.t.conn.execute("SELECT last_token, state FROM states WHERE key = ?", (key,)).fetchall()
    if r:
      [(token, state)] = r
      request.initial_token = token
      request.initial_state = pickle.loads(state)
    else:
      request.initial_token = self.default_token
      request.initial_state = None

  def backward(self, request):
    self.opendb()
    self.t.conn.execute("INSERT OR REPLACE INTO states (key, last_token, state) VALUES (?,?,?)", (request.key, request.last_token, pickle.dumps(request.final_state)))
    self.t.conn.commit()