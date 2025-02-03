from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Sample commands with their status
commands = {
    "kick": True,
    "ban": True,
    "mute": False,
    "unmute": True,
    "warn": False
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/commands", methods=["GET"])
def get_commands():
    return jsonify(commands)

@app.route("/update", methods=["POST"])
def update_command():
    data = request.json
    command = data.get("command")
    status = data.get("status")
    if command in commands:
        commands[command] = status
        return jsonify({"success": True, "command": command, "status": status})
    return jsonify({"success": False, "error": "Command not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
