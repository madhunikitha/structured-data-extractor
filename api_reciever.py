from flask import Flask, request, jsonify
from doc_input import extract_text1

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        text = extract_text1(file)
        return jsonify({"extracted_text": text})
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
