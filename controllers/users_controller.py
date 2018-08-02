import bcrypt
import server
from database import Cursor, Database as db

def get_users(page_size, page_index):
  try:
    with Cursor() as cur:
      cur.execute(
        "SELECT * FROM users "
        "WHERE type = 'regular' "
        "ORDER BY created_by ASC "
        "LIMIT %s OFFSET %s",
        (page_size, page_size * page_index)
      )

      if cur.rowcount:
        return server.ok(data=cur.fetchall())
      else:
        return server.not_found('no users found')
  except:
    return server.error('unable to get users')

def create_user(first_name, last_name, email, password, created_by):
  password_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()).decode('utf8')

  try:
    with Cursor() as cur:
      cur.execute(
        'INSERT INTO users '
          '(first_name, last_name, email, password, created_by) '
        'VALUES '
          '(%s, %s, %s, %s, %s) '
        'RETURNING *',
        (first_name, last_name, email, password_hash, created_by)
      )

      return server.ok(data=cur.fetchone())
  except:
    return server.error('unable to create user')