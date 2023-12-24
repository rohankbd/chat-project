import json
from channels.generic.websocket import AsyncWebsocketConsumer
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag

# Ensure NLTK resources are downloaded (do this once)
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')

# Define your color mapping based on the POS tags
# pos_color_map = {
#     'JJ': 'background-color: #FFB6C1;',  # Adjective
#     'RB': 'background-color: #FFD700;',  # Adverb
#     'CC': 'background-color: #FFA07A;',  # Conjunction
#     'DT': 'background-color: #7FFFD4;',  # Determiner
#     'NN': 'background-color: #87CEFA;',  # Noun
#     'CD': 'background-color: #32CD32;',  # Number
#     'IN': 'background-color: #BA55D3;',  # Preposition
#     'PRP': 'background-color: #FF69B4;', # Pronoun
#     'VB': 'background-color: #FFA500;',  # Verb
#     # ... add other tags as necessary
# }

pos_color_map = {
    'JJ': 'background-color: #FDCC65;',  # Adjective
    'RBS': 'background-color: #CC9998;',  # Adverb (Superlative)
    'RB': 'background-color: #CC9998;',  # Adverb
    'RBR': 'background-color: #CC9998;',  # Adverb (Comparative)
    'CC': 'background-color: #CCCD99;',  # Conjunction
    'DT': 'background-color: #9999CC;',  # Determiner
    'NN': 'background-color: #CCCCCC;',  # Noun (Singular)
    'NNS': 'background-color: #CCCCCC;',  # Noun (Plural)
    'NNP': 'background-color: #CCCCCC;',  # Proper Noun (Singular)
    'NNPS': 'background-color: #CCCCCC;',  # Proper Noun (Plural)
    'CD': 'background-color: #65CC99;',  # Number (Cardinal)
    'IN': 'background-color: #EA8CAE;',  # Preposition
    'PRP': 'background-color: #EEEE77;',  # Pronoun (Personal)
    'PRP$': 'background-color: #EEEE77;',  # Pronoun (Possessive)
    'WP': 'background-color: #EEEE77;',  # Pronoun (Wh)
    'WP$': 'background-color: #FF69B4;',  # Possessive Wh
    'WDT': 'background-color: #FF69B4;',  # Determiner of Wh
    'VBZ': 'background-color: #CCFF65;',  # Verb (3rd person singular present)
    'VBP': 'background-color: #CCFF65;',  # Verb (Non-3rd person singular present)
    'VBN': 'background-color: #CCFF65;',  # Verb (Past participle)
    'VBG': 'background-color: #CCFF65;',  # Verb (Gerund or present participle)
    'VBD': 'background-color: #CCFF65;',  # Verb (Past tense)
    'VB': 'background-color: #CCFF65;',  # Verb (Base form)
    # ... add other tags as necessary
}

def nltk_analysis_function(message):
    tokens = word_tokenize(message)
    tagged_tokens = pos_tag(tokens)
    
    colored_message = ""
    for word, tag in tagged_tokens:
        color_style = pos_color_map.get(tag, 'background-color: #FFFFFF;')  # Default color
        colored_message += f'<span style="{color_style}">{word}</span> '

    return colored_message.strip()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "chat_room_group",
            self.channel_name
        )
        await self.accept()
        await self.channel_layer.group_send(
            "chat_room_group",
            {
                "type": "chat_message",
                "message": "---Someone logged in---"
            }
        )

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Handle the special command for NLTK processing
        if message.startswith('analyze: '):
            # Process the message with NLTK here
            analysis_result = nltk_analysis_function(message[9:])
            await self.send(text_data=json.dumps({
                'message': analysis_result
            }))
        else:
    # Echo message back to sender
            # await self.send(text_data=json.dumps({
            #     'message': message
            # }))
            # Broadcast message to room group
            await self.channel_layer.group_send(
                "chat_room_group",
                {
                    "type": "chat_message",
                    "message": message,
                }
            )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))