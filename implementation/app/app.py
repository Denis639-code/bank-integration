from app import create_app

app = create_app()


@app.route("/")
def home():
    return "hello, world"


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
