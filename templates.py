"""
Template multilingua per i messaggi del bot
Include template per i post sui canali in diverse lingue
"""

from typing import Dict
from config import CATEGORIES


def hide_link(url: str, text: str) -> str:
    """
    Nasconde un URL dietro un testo cliccabile (Hyperlink Markdown per Telegram)
    
    Args:
        url: L'URL completo da nascondere
        text: Il testo da mostrare all'utente
        
    Returns:
        String formattata come hyperlink per Telegram
    """
    return f"[{text}]({url})"


def create_post_caption(
    product_name: str,
    price: str,
    referral_link: str,
    category: str,
    language: str
) -> str:
    """
    Crea la didascalia per il post del prodotto nella lingua specificata
    
    Args:
        product_name: Nome del prodotto
        price: Prezzo del prodotto
        referral_link: Link di affiliazione
        category: Categoria del prodotto (es. 'shoes', 'clothing')
        language: Codice lingua ('IT', 'EN', 'ES')
        
    Returns:
        Didascalia formattata per Telegram con Markdown
    """
    
    # Recupera i dati della categoria per la lingua specificata
    cat_data = CATEGORIES.get(category, CATEGORIES['clothing']).get(language, {})
    emoji = cat_data.get('emoji', '✨')
    hashtag = cat_data.get('hashtag', '#FASHION')
    
    # Template specifici per lingua con hyperlink nascosto
    templates = {
        'IT': f"""🔥 {emoji} *{product_name}* {emoji}

💰 *Prezzo:* {price}

{hashtag} #Fashion #Style #Shopping

✅ Qualità Premium
🚚 Spedizione Rapida
💯 Garanzia Soddisfazione

👉 {hide_link(referral_link, "CLICCA QUI PER ACQUISTARE")}

💬 _Seguici per altri deal esclusivi!_
""",
        
        'EN': f"""🔥 {emoji} *{product_name}* {emoji}

💰 *Price:* {price}

{hashtag} #Fashion #Style #Shopping

✅ Premium Quality
🚚 Fast Shipping
💯 Satisfaction Guaranteed

👉 {hide_link(referral_link, "CLICK HERE TO BUY")}

💬 _Follow us for more exclusive deals!_
""",
        
        'ES': f"""🔥 {emoji} *{product_name}* {emoji}

💰 *Precio:* {price}

{hashtag} #Moda #Estilo #Compras

✅ Calidad Premium
🚚 Envío Rápido
💯 Garantía de Satisfacción

👉 {hide_link(referral_link, "CLIC AQUÍ PARA COMPRAR")}

💬 _¡Síguenos para más ofertas exclusivas!_
"""
    }
    
    return templates.get(language, templates['EN'])


def get_bot_messages(language: str = 'IT') -> Dict[str, str]:
    """
    Restituisce i messaggi del bot nella lingua specificata
    
    Args:
        language: Codice lingua ('IT', 'EN', 'ES')
        
    Returns:
        Dizionario con tutti i messaggi del bot
    """
    
    messages = {
        'IT': {
            'welcome': """
👋 *Benvenuto nel Bot di Affiliate Marketing!*

Inviami un gruppo di foto (Media Group) insieme al link del prodotto con il tuo codice referral già inserito.

Io farò il resto! ✨
""",
            'unauthorized': "⛔ Non sei autorizzato ad usare questo bot.",
            
            'scraping_started': "🔍 Sto analizzando il link per estrarre le informazioni del prodotto...",
            
            'scraping_success': "✅ Informazioni estratte con successo!\n\n📦 *Prodotto:* {product}\n💰 *Prezzo:* {price}",
            
            'scraping_failed': """
⚠️ Non sono riuscito ad estrarre il prezzo automaticamente.

Per favore, inviami il prezzo del prodotto manualmente (es. ¥199 o $29.99)
""",
            
            'select_category': "📂 Seleziona la categoria del prodotto:",
            
            'invalid_price': "❌ Formato prezzo non valido. Riprova (es. ¥199 o $29.99)",
            
            'preview_intro': "👀 *Anteprima Post*\n\nEcco come apparirà il post nei vari canali:",
            
            'preview_channel': "\n🌍 *Canale {flag} {name}:*\n",
            
            'confirm_publish': "✅ Confermi la pubblicazione su tutti i canali?",
            
            'publishing': "📤 Sto pubblicando sui canali...",
            
            'publish_success': "✅ Post pubblicato con successo su {channel}!",
            
            'publish_error': "❌ Errore nella pubblicazione su {channel}: {error}",
            
            'publish_complete': "🎉 Pubblicazione completata!\n\n{summary}",
            
            'cancelled': "❌ Operazione annullata.",
            
            'error_generic': "❌ Si è verificato un errore: {error}",
            
            'need_media_and_link': "⚠️ Inviami un gruppo di foto insieme al link del prodotto nel messaggio.",
            
            'button_confirm': "✅ Conferma e Pubblica",
            'button_cancel': "❌ Annulla"
        },
        
        'EN': {
            'welcome': """
👋 *Welcome to the Affiliate Marketing Bot!*

Send me a media group (photos) along with the product link containing your referral code.

I'll take care of the rest! ✨
""",
            'unauthorized': "⛔ You are not authorized to use this bot.",
            
            'scraping_started': "🔍 Analyzing the link to extract product information...",
            
            'scraping_success': "✅ Information extracted successfully!\n\n📦 *Product:* {product}\n💰 *Price:* {price}",
            
            'scraping_failed': """
⚠️ Couldn't extract the price automatically.

Please send me the product price manually (e.g., ¥199 or $29.99)
""",
            
            'select_category': "📂 Select product category:",
            
            'invalid_price': "❌ Invalid price format. Try again (e.g., ¥199 or $29.99)",
            
            'preview_intro': "👀 *Post Preview*\n\nHere's how the post will appear on different channels:",
            
            'preview_channel': "\n🌍 *Channel {flag} {name}:*\n",
            
            'confirm_publish': "✅ Confirm publication on all channels?",
            
            'publishing': "📤 Publishing to channels...",
            
            'publish_success': "✅ Successfully published on {channel}!",
            
            'publish_error': "❌ Error publishing to {channel}: {error}",
            
            'publish_complete': "🎉 Publication complete!\n\n{summary}",
            
            'cancelled': "❌ Operation cancelled.",
            
            'error_generic': "❌ An error occurred: {error}",
            
            'need_media_and_link': "⚠️ Send me a media group with the product link in the message.",
            
            'button_confirm': "✅ Confirm and Publish",
            'button_cancel': "❌ Cancel"
        },
        
        'ES': {
            'welcome': """
👋 *¡Bienvenido al Bot de Marketing de Afiliados!*

Envíame un grupo de fotos junto con el enlace del producto con tu código de referencia ya incluido.

¡Yo me encargo del resto! ✨
""",
            'unauthorized': "⛔ No estás autorizado para usar este bot.",
            
            'scraping_started': "🔍 Analizando el enlace para extraer información del producto...",
            
            'scraping_success': "✅ ¡Información extraída con éxito!\n\n📦 *Producto:* {product}\n💰 *Precio:* {price}",
            
            'scraping_failed': """
⚠️ No pude extraer el precio automáticamente.

Por favor, envíame el precio del producto manualmente (ej. ¥199 o $29.99)
""",
            
            'select_category': "📂 Selecciona la categoría del producto:",
            
            'invalid_price': "❌ Formato de precio inválido. Inténtalo de nuevo (ej. ¥199 o $29.99)",
            
            'preview_intro': "👀 *Vista previa del Post*\n\nAsí es como aparecerá el post en los diferentes canales:",
            
            'preview_channel': "\n🌍 *Canal {flag} {name}:*\n",
            
            'confirm_publish': "✅ ¿Confirmas la publicación en todos los canales?",
            
            'publishing': "📤 Publicando en los canales...",
            
            'publish_success': "✅ ¡Publicado con éxito en {channel}!",
            
            'publish_error': "❌ Error al publicar en {channel}: {error}",
            
            'publish_complete': "🎉 ¡Publicación completa!\n\n{summary}",
            
            'cancelled': "❌ Operación cancelada.",
            
            'error_generic': "❌ Ocurrió un error: {error}",
            
            'need_media_and_link': "⚠️ Envíame un grupo de fotos con el enlace del producto en el mensaje.",
            
            'button_confirm': "✅ Confirmar y Publicar",
            'button_cancel': "❌ Cancelar"
        }
    }
    
    return messages.get(language, messages['IT'])


# Messaggi di sistema (sempre in italiano per l'admin)
SYSTEM_MESSAGES = {
    'start_bot': "🤖 Bot avviato con successo!",
    'stop_bot': "🛑 Bot arrestato.",
    'channel_unreachable': "⚠️ Impossibile raggiungere il canale {channel}. Verifica le impostazioni.",
    'driver_error': "❌ Errore del driver Selenium. Assicurati che Chrome e ChromeDriver siano installati correttamente."
}


if __name__ == "__main__":
    # Test dei template
    print("=== TEST TEMPLATE ITALIANO ===")
    caption_it = create_post_caption(
        product_name="Nike Air Jordan 1 High",
        price="¥399",
        referral_link="https://www.oopbuy.com/product/?url=https://weidian.com/item.html?itemID=123456&inviteCode=ABC123",
        category="shoes",
        language="IT"
    )
    print(caption_it)
    
    print("\n=== TEST TEMPLATE INGLESE ===")
    caption_en = create_post_caption(
        product_name="Nike Air Jordan 1 High",
        price="¥399",
        referral_link="https://www.oopbuy.com/product/?url=https://weidian.com/item.html?itemID=123456&inviteCode=ABC123",
        category="shoes",
        language="EN"
    )
    print(caption_en)
