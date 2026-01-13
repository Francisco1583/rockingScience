from rocket_app.app import create_app

app = create_app()
server = app.server

if __name__ == "__main__":
    app.run(debug=True, port=1234)
