from flask import Flask, render_template, request, jsonify
from analysis import analyze_safety, calculate_energy, analyze_components
from chatbot import get_chatbot_response

app = Flask(__name__)

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    safety_result = analyze_safety(data.get('safety', {}))
    energy_result = calculate_energy(data.get('energy', {}))
    component_result = analyze_components(data.get('components', {}))
    
    return jsonify({
        "safety": safety_result,
        "energy": energy_result,
        "components": component_result
    })

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('message', '')
    file = request.files.get('file')
    
    file_content = None
    filename = None
    if file:
        filename = file.filename
        # In a real app, we'd save and process. Here we just read if it's text, 
        # or simulate analysis of drawing plans.
        try:
            file_content = file.read().decode('utf-8', errors='ignore')
        except:
            file_content = "[Binary/Drawing File]"
            
    bot_response = get_chatbot_response(user_message, filename, file_content)
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)
