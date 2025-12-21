"""
Configurazione del Telegram Bot per Affiliate Marketing
Questo file contiene tutte le configurazioni necessarie per il bot
"""

import os
from dotenv import load_dotenv

# Carica variabili d'ambiente da file .env
load_dotenv()

# ============================================
# CONFIGURAZIONE BOT
# ============================================

# Token del bot Telegram (da ottenere da @BotFather)
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Il tuo User ID Telegram (per sicurezza)
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))  # Sostituisci con il tuo ID

# ============================================
# CONFIGURAZIONE CANALI
# ============================================

# Dizionario con i canali per ogni lingua
CHANNELS = {
    'IT': {
        'chat_id': os.getenv('CHANNEL_IT', '@your_italian_channel'),
        'name': 'Italiano',
        'emoji_flag': '🇮🇹'
    },
    'EN': {
        'chat_id': os.getenv('CHANNEL_EN', '@your_english_channel'),
        'name': 'English',
        'emoji_flag': '🇬🇧'
    },
    'ES': {
        'chat_id': os.getenv('CHANNEL_ES', '@your_spanish_channel'),
        'name': 'Español',
        'emoji_flag': '🇪🇸'
    }
}

# ============================================
# CATEGORIE PRODOTTI
# ============================================

CATEGORIES = {
    'shoes': {
        'IT': {'name': 'Scarpe', 'hashtag': '#SCARPE', 'emoji': '👟'},
        'EN': {'name': 'Shoes', 'hashtag': '#SHOES', 'emoji': '👟'},
        'ES': {'name': 'Zapatos', 'hashtag': '#ZAPATOS', 'emoji': '👟'}
    },
    'clothing': {
        'IT': {'name': 'Abbigliamento', 'hashtag': '#ABBIGLIAMENTO', 'emoji': '👕'},
        'EN': {'name': 'Clothing', 'hashtag': '#CLOTHING', 'emoji': '👕'},
        'ES': {'name': 'Ropa', 'hashtag': '#ROPA', 'emoji': '👕'}
    },
    'accessories': {
        'IT': {'name': 'Accessori', 'hashtag': '#ACCESSORI', 'emoji': '👜'},
        'EN': {'name': 'Accessories', 'hashtag': '#ACCESSORIES', 'emoji': '👜'},
        'ES': {'name': 'Accesorios', 'hashtag': '#ACCESORIOS', 'emoji': '👜'}
    },
    'bags': {
        'IT': {'name': 'Borse', 'hashtag': '#BORSE', 'emoji': '🎒'},
        'EN': {'name': 'Bags', 'hashtag': '#BAGS', 'emoji': '🎒'},
        'ES': {'name': 'Bolsas', 'hashtag': '#BOLSAS', 'emoji': '🎒'}
    },
    'watches': {
        'IT': {'name': 'Orologi', 'hashtag': '#OROLOGI', 'emoji': '⌚'},
        'EN': {'name': 'Watches', 'hashtag': '#WATCHES', 'emoji': '⌚'},
        'ES': {'name': 'Relojes', 'hashtag': '#RELOJES', 'emoji': '⌚'}
    }
}

# ============================================
# CONFIGURAZIONE WEB SCRAPING
# ============================================

# Timeout per lo scraping (in secondi)
SCRAPING_TIMEOUT = 15

# User-Agent per le richieste
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# ============================================
# STATI CONVERSATION HANDLER
# ============================================

# Stati del flusso conversazionale
STATE_WAITING_CATEGORY = 1
STATE_WAITING_PRICE = 2
STATE_PREVIEW = 3
STATE_CONFIRM = 4
STATE_WAITING_PHOTOS = 5
STATE_WAITING_PRODUCT_NAME = 6
# ============================================
# LOGGING
# ============================================

# Livello di logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
