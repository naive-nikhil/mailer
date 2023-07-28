from app import app
from flask import session


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8178)
