import bcrypt
import jwt
import os
import server
from database import Cursor, Database as db

def login(email, password, auth_type):
  try:
    with Cursor() as cur:
      cur.execute('SELECT * FROM users WHERE email = %s and type = %s', (email, auth_type))

      if cur.rowcount:
        user = cur.fetchone()
        data = {}
        data['user'] = user

        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
          data['auth_token'] = jwt.encode({}, os.environ.get('JWT_SIGNING_KEY'),
            algorithm='HS256').decode('utf-8')
          return server.ok(data=data)
        else:
          return server.bad_req('incorrect password')
      else:
        return server.bad_req("account doesn't exist")
  except:
    return server.error('unable to login')
