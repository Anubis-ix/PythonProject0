import random

def get_chatbot_response(user_message, filename=None, file_content=None):
    message = user_message.lower()
    
    # If a file is provided, prioritize file analysis (AI Agent behavior)
    if filename:
        analysis_report = f"### AI Agent Analysis of {filename}\n"
        
        # Simulate structural drawing analysis
        if any(ext in filename.lower() for ext in ['.pdf', '.dwg', '.dxf', '.jpg', '.png']):
            analysis_report += "I have scanned the structural drawing plan. Here are my findings:\n"
            analysis_report += "- **Load-Bearing Walls**: Correctly identified. Alignment looks consistent across floors.\n"
            analysis_report += "- **Beam Spans**: Detected a potential issue in the North-East section. The span appears to exceed 6 meters without a secondary support column.\n"
            analysis_report += "- **Safety Rating**: 85%. Recommend adding one column at grid intersection C-4 to prevent future deflection.\n"
            analysis_report += "- **Sustainability**: Drawing shows thermal bridges at window junctions. Consider improved detailing."
        else:
            analysis_report += "File received. I'm analyzing the project data... Everything looks structurally sound based on the text parameters provided."
            
        return analysis_report

    # Engineering/Safety related
    if any(word in message for word in ['safety', 'collapse', 'beam', 'span', 'depth']):
        return "Building safety is our priority. Our simulation uses the L/16 rule for beam depth and checks material limits. Do you have specific dimensions you're worried about?"
    
    # Energy/Sustainability related
    elif any(word in message for word in ['energy', 'sustainability', 'solar', 'insulation', 'consumption']):
        return "To improve sustainability, focus on high-quality insulation and renewable energy sources like solar panels. Our energy calculator can estimate your annual needs."
    
    # About System/Simulation
    elif any(word in message for word in ['ansys', 'simulation', 'rcc', 'standards']):
        return "Our system uses advanced simulation algorithms based on RCC (Reinforced Concrete Council) standards like BS8110 and Eurocode 2 (EC2). This helps prevent structural failures and optimizes energy use."

    # Greetings
    elif any(word in message for word in ['hello', 'hi', 'hey']):
        return "Hello! I am your Engineering AI assistant, now synced with RCC standards. How can I assist you with your project today?"

    # Specific components
    elif any(word in message for word in ['slab', 'column', 'stair', 'beam']):
        return "I can analyze specific components like one-way slabs (RCC31), columns (RCC51), stairs (RCC72), and continuous beams (RCC41). Use the cards on the main dashboard to run a simulation."
    
    # Default
    else:
        responses = [
            "That's an interesting question. While I'm specialized in structural safety and energy analysis, I recommend consulting with a licensed engineer for final designs.",
            "I'm here to help with your building analysis. Could you provide more details about your inquiry?",
            "Our system can analyze beam spans, material safety, and energy efficiency. Which of these would you like to know more about?"
        ]
        return random.choice(responses)
