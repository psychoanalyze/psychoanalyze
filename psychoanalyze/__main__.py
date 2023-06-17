from .dashboard.app import app


def main():
    app.run(
        host="localhost",
        debug=True,
    )


if __name__ == "__main__":
    main()
