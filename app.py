from flask import Flask, jsonify, make_response, request, abort


app = Flask(__name__)



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/chat', methods=['POST'])
def chat_route():
	print(request.json)
	if not request.json or not 'title' in request.json:
		abort(400)
	return jsonify({'response': "POST"}), 201


if __name__ == '__main__':
    app.run(debug=True)