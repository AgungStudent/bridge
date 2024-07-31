from flask import Flask, render_template

app = Flask(__name__)

#=====MITRA=====

@app.route("/mitra/stock")
def mitra_stock():
    return render_template("/mitra/mitra-stock.html")

@app.route("/mitra/branch")
def mitra_branch():
    return render_template("/mitra/mitra-branch.html")

@app.route("/mitra/history")
def mitra_history():
    return render_template("/mitra/mitra-history.html")

@app.route("/mitra/sign-in")
def mitra_signin():
    return render_template("/mitra/mitra-signin.html")

@app.route("/mitra/sign-up")
def mitra_signup():
    return render_template("/mitra/mitra-signup.html")

#=====USER=====

@app.route("/user/history")
def user_history():
    return render_template("/user/user-history.html")

@app.route("/user/mitra")
def user_mitra():
    return render_template("/user/user-mitra.html")

@app.route("/user/sign-up")
def user_signup():
    return render_template("/user/user-signup.html")

@app.route("/user/sign-in")
def user_signin():
    return render_template("/user/user-signin.html")

if __name__ == "__main__":
    print("from main")
    app.run(port=8081, debug=True, host="localhost")