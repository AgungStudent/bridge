from flask import Flask, render_template

app = Flask(__name__)

#=====MITRA=====

@app.route("/mitra/stock")
def mitra_stock():
    return render_template("/mitra/mitra-stock.html")

@app.route("/mitra/branch")
def mitra_branch():
    return render_template("/mitra/mitra-branch.html")

@app.route("/mitra/sign-in")
def mitra_signin():
    return render_template("/mitra/mitra-signin.html")

@app.route("/mitra/sign-up")
def mitra_signup():
    return render_template("/mitra/mitra-signup.html")

if __name__ == "__main__":
    print("from main")
    app.run(port=8081, debug=True, host="localhost")