from flask import Flask

from controller.mitra import mitra_history

app = Flask(__name__)


@app.get("/dummy-history")
def history():
    mitra_history.history()
    return ""


app.run(debug=True)
