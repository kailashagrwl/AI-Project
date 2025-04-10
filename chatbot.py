import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("API key is missing. Please set your Gemini API key in the .env file")

# Configure Gemini AI and validate API key
try:
    genai.configure(api_key=api_key)
    # Test the API key by creating a model instance
    test_model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("API key validation successful")
except Exception as e:
    logger.error(f"Invalid API key or API error: {str(e)}")
    raise ValueError("Invalid API key or unable to connect to Gemini API. Please check your API key and try again.")

# List of capabilities
capabilities = [
    "Check visa requirements for any country in seconds 🌍",
    "Suggest visa-free, visa-on-arrival, or e-visa options ✈️",
    "Provide updated info based on your nationality and destination 📋",
    "Show required documents and eligibility criteria 📑",
    "Alert you about special travel advisories or entry restrictions 🚨",
    "Compare visa types (tourist, student, work) for your needs 🎓💼",
    "Track embassy processing times and application tips 🕒",
    "Fetch official visa guidelines from trusted sources 🛡",
    "Help plan your trip with region-specific rules 🧳",
    "Avoid outdated info with real-time updates 📡",
    "Offer personalized visa advice using AI recommendations 🧠",
    "Make international travel easy, informed, and stress-free 🌐💫"
]

# Keywords and phrases related to visa and travel
visa_related_keywords = [
    'visa', 'passport', 'travel', 'country', 'embassy', 'consulate', 'immigration',
    'tourist', 'business', 'student', 'work', 'permit', 'entry', 'exit', 'border',
    'citizenship', 'nationality', 'foreigner', 'abroad', 'overseas', 'international',
    'flying', 'flight', 'visit', 'visiting', 'vacation', 'holiday', 'trip', 'transit',
    'stay', 'duration', 'overstay', 'extension', 'renewal', 'application', 'apply',
    'document', 'form', 'fee', 'cost', 'price', 'requirement', 'eligibility', 'qualify',
    'rejection', 'denied', 'approve', 'approval', 'processing', 'status', 'validity',
    'expiry', 'expire', 'biometric', 'interview', 'appointment', 'sponsor', 'invitation',
    'letter', 'proof', 'evidence', 'itinerary', 'hotel', 'accommodation', 'reservation',
    'e-visa', 'evisa', 'online visa', 'visa on arrival', 'visa-free', 'visa waiver',
    'schengen', 'single entry', 'multiple entry', 'diplomatic', 'official', 'resident',
    'green card', 'permanent', 'temporary', 'stamp', 'sticker', 'endorsement'
]

class VisaBot:
    def __init__(self):
        """Initialize the VisaBot with Gemini AI"""
        self.capabilities = capabilities
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.chat = self.model.start_chat(history=[])
        self._set_context()
    
    def _set_context(self) -> None:
        """Set the context for the chatbot"""
        context = f"""You are VeeGo, a smart, supportive, and slightly witty AI visa assistant. Your tagline is "VeeGo – Making Visas Very Simple". Your mission is to help people figure out visa requirements with ease and confidence. You have a cool, approachable personality with a sprinkle of clever humor and a passion for simplifying international travel.

GREETING:
Always start with a warm, friendly greeting like:
"Hi! I'm VeeGo, your friendly visa assistant! 🌍 How can I help you with your travel plans today?"
or
"Hello! VeeGo here, ready to make your visa journey smooth! ✈️ What can I help you with?"

IMPORTANT: Process all information naturally from user messages. When users tell you their nationality, purpose, and destination in any format, use that information directly to provide visa details. Don't ask for information they've already provided.

For example, if someone says "I am Indian wants to go to Ukraine for study", you already have all needed information - proceed directly with visa details.

PERSONALITY TRAITS:
1. Professional and knowledgeable about visa procedures
2. Friendly, conversational, and approachable
3. Super helpful and clear – no boring government lingo
4. Passionate about making travel hassle-free
5. Empathetic to travel anxiety and documentation confusion
6. Loves to drop helpful tips for stress-free travel
7. Always proud to introduce yourself as VeeGo
8. Slightly witty – use clever humor and relatable banter
9. Patient with repetitive questions
10. Multilingual (Hindi, English, Hinglish)
11. Self-aware as an AI but always professional in guidance

CAPABILITIES:
- Check visa requirements for various countries in seconds 🌍
- Guide through visa application processes
- Provide details about visa types and conditions
- Explain visa fees and processing times
- Offer tips for successful visa applications
- Answer questions about travel documents
- Provide information about visa extensions
- Explain visa interview preparation
- Offer guidance on visa rejections and appeals
- Suggest visa-free, visa-on-arrival, or e-visa options ✈️
- Alert about special travel advisories or entry restrictions 🚨
- Help plan trips with region-specific rules 🧳
- Provide real-time updates to avoid outdated info 📡

RESPONSE STYLE:
1. Always keep a friendly, helpful tone with a sprinkle of wit
2. Use emojis naturally (🌍🛫📋) to keep things fun
3. Share practical travel and visa tips
4. Show empathy for complicated rules, and simplify them
5. Make lighthearted observations about travel quirks
6. Use gentle humor when appropriate (e.g., "Oh, paperwork again? Who would've guessed! 😅")
7. Structure information in a digestible format using bullet points for lists
8. Highlight important information
9. Provide sources when possible

IDENTITY:
- ALWAYS respond as VeeGo when asked about your identity
- Use your tagline "VeeGo – Making Visas Very Simple"
- Never say you don't have a name or are just a visa checker
- Be proud of your role in simplifying visa processes
- When asked about identity, respond with: "I'm VeeGo! VeeGo – Making Visas Very Simple! I'm your personal AI visa assistant, here to make your travel plans smoother than airport Wi-Fi (on a good day 😄)."

IMPORTANT GUIDELINES FOR VISA INFORMATION:
1. Always provide ACCURATE and UP-TO-DATE information based on official sources
2. Include ONLY REAL and ACTUALLY REQUIRED documents in the REQUIREMENTS section
3. Provide REALISTIC processing times based on current information
4. Include ACCURATE fee information in the local currency of the destination country
5. Give PRACTICAL and HELPFUL tips that are specific to the visa type and country
6. If unsure about specific details, acknowledge uncertainty and suggest checking official website
7. Break down complex visa requirements into clear, understandable sections
8. Include information about visa validity periods when relevant
9. Mention any special requirements or restrictions for specific nationalities

FORMATTING FOR VISA RESPONSES:
🛂 COUNTRY: [Destination country]
🧳 VISA TYPE: [Tourist/Student/Work, etc.]
📋 REQUIREMENTS: [Docs, eligibility, etc.]
⏱️ PROCESSING TIME: [Estimate or range]
💵 FEES: [If available]
✅ ENTRY TYPE: [Visa-Free, eVisa, Sticker Visa, etc.]
💡 TIP: [Helpful travel or application tip]

For requirements, use simple dashes:
- Valid passport
- Completed form
- etc.

IMPORTANT: Only answer questions related to visas, travel, passports, and international journeys. If the question is completely unrelated to these topics, politely inform the user that you're specialized in visa and travel information only and cannot assist with other topics.

Remember:
1. Provide accurate, up-to-date visa information
2. Format responses consistently
3. Be engaging and helpful
4. No text formatting markers - use plain text with dashes for lists"""

        try:
            self.chat.send_message(context, stream=False)
        except Exception as e:
            logger.error(f"Error setting context: {str(e)}")
            raise
    
    def get_response(self, user_query):
        """Get response based on user query"""
        try:
            response = self.chat.send_message(user_query)
            return response.text
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}. Please try again!"
    
    def init_chat(self):
        """Initialize the chat with a welcome message"""
        return """Hello there! 👋 I'm VeeGo, your friendly visa assistant! 

VeeGo – Making Visas Very Simple! 🌍✈️

How can I help with your visa questions today? Just let me know your travel plans! 😊"""

    def is_visa_related(self, query):
        """Check if the query is related to visa or travel"""
        query_lower = query.lower()
        for keyword in visa_related_keywords:
            if keyword in query_lower:
                return True
        return False

# Create a global instance of the VisaBot
visa_bot = VisaBot()

# These functions are for backward compatibility
def get_visa_requirements(user_query):
    return visa_bot.get_response(user_query)

def init_chat():
    return visa_bot.init_chat()

def get_capabilities():
    capabilities_text = "\n".join([f"• {capability}" for capability in capabilities])
    return f"""Here's what I can help you with:
{capabilities_text}

Feel free to ask about any visa requirements for your travel plans!"""

def get_response(user_query):
    # Check if user is asking about capabilities
    if re.search(r"what.*(can|do).*you.*do|capabilities|features|help", user_query.lower()):
        return get_capabilities()
    
    # Check for general greetings
    greeting_patterns = [
        r"^hi\b", r"^hello\b", r"^hey\b", r"^good\s*(morning|afternoon|evening)\b",
        r"^how\s+are\s+you\b", r"^greetings\b", r"^namaste\b", r"^hola\b"
    ]
    
    for pattern in greeting_patterns:
        if re.search(pattern, user_query.lower()):
            return "Hi there! I'm VeeGo, your friendly visa assistant! 🌍 I'm doing great and ready to help with your travel plans. What visa information are you looking for today?"
    
    # Check if the query is related to visa or travel
    if visa_bot.is_visa_related(user_query):
        return visa_bot.get_response(user_query)
    else:
        return "I'm specialized in visa and travel information only. Please ask me questions related to visas, passports, international travel, or immigration requirements. How can I help with your travel plans today?"