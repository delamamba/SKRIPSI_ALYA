import app

app.load_model()
app.app.run(host="0.0.0.0", port=5001, debug=False)
