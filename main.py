from server.app import app
from server.commands import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
