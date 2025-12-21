"""
Telegram Bot per Affiliate Marketing - Main File
Bot multilingua per pubblicare prodotti su diversi canali Telegram
"""

import logging
import re
import asyncio
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode
import os

# Import configurazioni e moduli personalizzati
from config import (
    BOT_TOKEN,
    ADMIN_USER_ID,
    CHANNELS,
    CATEGORIES,
    STATE_WAITING_CATEGORY,
    STATE_WAITING_PRICE,
    STATE_PREVIEW,
    STATE_CONFIRM,
    STATE_WAITING_PHOTOS,
    STATE_WAITING_PRODUCT_NAME,
    LOG_LEVEL,
    LOG_FORMAT
)
from scraper import ProductScraper
from templates import create_post_caption, get_bot_messages, SYSTEM_MESSAGES

# Configurazione logging
logging.basicConfig(
    format=LOG_FORMAT,
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)


class AffiliateBot:
    """Classe principale del bot per affiliate marketing"""
    
    def __init__(self):
        """Inizializza il bot"""
        self.scraper = ProductScraper()
        self.messages = get_bot_messages('IT')  # Messaggi in italiano per l'admin
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handler per il comando /start
        Verifica l'autorizzazione dell'utente
        """
        user_id = update.effective_user.id
        
        # Verifica se l'utente è autorizzato
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text(
                self.messages['unauthorized'],
                parse_mode=ParseMode.MARKDOWN
            )
            logger.warning(f"Tentativo di accesso non autorizzato da user_id: {user_id}")
            return ConversationHandler.END
        
        # Benvenuto all'admin
        await update.message.reply_text(
            self.messages['welcome'],
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Admin {user_id} ha avviato il bot")
        return ConversationHandler.END
    
    async def _process_media_group(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa il media group dopo che tutte le foto sono arrivate"""
        job = context.job
        media_group_id = job.data['media_group_id']
        chat_id = job.data['chat_id']
        
        # Controlla se il gruppo esiste ancora
        if media_group_id not in context.user_data.get('media_groups', {}):
            logger.info(f"Media group {media_group_id}: non trovato in user_data")
            return
        
        # Salva le foto raccolte
        context.user_data['photos'] = context.user_data['media_groups'][media_group_id]['photos']
        num_photos = len(context.user_data['photos'])
        logger.info(f"Media group {media_group_id}: JOB ESEGUITO - completato con {num_photos} foto")
        
        # Rimuovi il gruppo processato
        del context.user_data['media_groups'][media_group_id]
        
        # Invia il messaggio di conferma
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ {num_photos} foto ricevuta/e!\n\n✏️ Scrivi il nome del prodotto:"
        )

    async def handle_media_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handler per ricevere gruppo di foto o solo link
        Fase 1 del flusso: se non arrivano foto prova a scaricarle dal link
        """
        user_id = update.effective_user.id
        
        # Verifica autorizzazione
        if user_id != ADMIN_USER_ID:
            return ConversationHandler.END
        
        message = update.message
        caption_or_text = (message.caption or message.text or "").strip()
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', caption_or_text)

        # Inizializza storage se è la prima volta
        if 'photos' not in context.user_data:
            context.user_data['photos'] = []
            context.user_data['media_groups'] = {}

        # Se è parte di un media group
        if message.media_group_id:
            media_group_id = message.media_group_id
            
            # Salva il link se presente (solo dalla prima foto del gruppo)
            if urls and not context.user_data.get('referral_link'):
                context.user_data['referral_link'] = urls[0]
            
            # Inizializza il gruppo se non esiste
            if media_group_id not in context.user_data['media_groups']:
                context.user_data['media_groups'][media_group_id] = {'photos': []}
            
            # Aggiungi foto al gruppo
            if message.photo:
                photo = message.photo[-1]
                context.user_data['media_groups'][media_group_id]['photos'].append(photo.file_id)
                logger.info(f"Media group {media_group_id}: aggiunta foto {len(context.user_data['media_groups'][media_group_id]['photos'])}")
            
            # Rimuovi job precedente se esiste
            job_name = f"media_group_{media_group_id}"
            current_jobs = context.job_queue.get_jobs_by_name(job_name)
            for job in current_jobs:
                logger.info(f"Media group {media_group_id}: rimosso job precedente")
                job.schedule_removal()
            
            # Schedula nuovo job per processare il gruppo tra 3 secondi (aumentato per aspettare tutte le foto)
            logger.info(f"Media group {media_group_id}: schedula job tra 3 secondi")
            context.job_queue.run_once(
                self._process_media_group,
                when=3.0,
                data={'media_group_id': media_group_id, 'chat_id': message.chat_id},
                name=job_name,
                chat_id=message.chat_id,
                user_id=user_id
            )
            
            # Non rispondere subito, aspetta che il job processi tutto
            return STATE_WAITING_PRODUCT_NAME
        
        # Messaggio singolo (non parte di un media group)
        else:
            # Aggiungi foto se presente
            if message.photo:
                photo = message.photo[-1]
                context.user_data['photos'].append(photo.file_id)
        
        # Verifica se abbiamo link
        if not urls and not context.user_data.get('referral_link'):
            await message.reply_text(self.messages['need_media_and_link'])
            context.user_data.clear()
            return ConversationHandler.END
        
        # Salva il link se non già salvato
        if urls and not context.user_data.get('referral_link'):
            context.user_data['referral_link'] = urls[0]

        # Se non ci sono foto, chiedi foto
        if not context.user_data['photos']:
            await message.reply_text("📸 Inviami le foto del prodotto (puoi mandarne fino a 10).")
            return STATE_WAITING_PHOTOS

        # Chiedi nome prodotto
        await message.reply_text(f"✅ {len(context.user_data['photos'])} foto ricevuta/e!\n\n✏️ Scrivi il nome del prodotto:")
        return STATE_WAITING_PRODUCT_NAME
    
    async def ask_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Chiede all'utente di selezionare la categoria
        Fase 2 del flusso
        """
        # Crea la tastiera con le categorie
        keyboard = []
        for cat_key, cat_values in CATEGORIES.items():
            cat_name_it = cat_values['IT']['name']
            emoji = cat_values['IT']['emoji']
            keyboard.append([
                InlineKeyboardButton(
                    f"{emoji} {cat_name_it}",
                    callback_data=f"cat_{cat_key}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Invia il messaggio o modifica quello esistente
        if update.callback_query:
            await update.callback_query.message.reply_text(
                self.messages['select_category'],
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                self.messages['select_category'],
                reply_markup=reply_markup
            )
        
        return STATE_WAITING_CATEGORY
    
    async def handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handler per la selezione della categoria
        """
        query = update.callback_query
        await query.answer()
        
        # Estrai la categoria
        category = query.data.replace('cat_', '')
        context.user_data['category'] = category
        
        logger.info(f"Categoria selezionata: {category}")
        
        # Conferma la selezione
        cat_name = CATEGORIES[category]['IT']['name']
        await query.edit_message_text(f"✅ Categoria selezionata: {cat_name}")
        
        # Passa all'anteprima
        return await self.show_preview(update, context)
    
    async def handle_product_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handler per il nome prodotto inserito manualmente
        """
        product_name = update.message.text.strip()
        
        if not product_name:
            await update.message.reply_text("⚠️ Il nome prodotto non può essere vuoto. Riprova:")
            return STATE_WAITING_PRODUCT_NAME
        
        # Salva il nome prodotto
        context.user_data['product_name'] = product_name
        logger.info(f"Nome prodotto inserito: {product_name}")
        
        await update.message.reply_text(f"✅ Nome salvato: {product_name}\n\n💰 Ora scrivi il prezzo (es: $49.99, €35, 299¥):")
        
        return STATE_WAITING_PRICE
    
    async def handle_manual_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handler per il prezzo inserito manualmente
        """
        price_text = update.message.text.strip()
        
        # Valida il formato del prezzo (deve contenere numeri)
        if not any(c.isdigit() for c in price_text):
            await update.message.reply_text(self.messages['invalid_price'])
            return STATE_WAITING_PRICE
        
        # Salva il prezzo
        context.user_data['price'] = price_text
        logger.info(f"Prezzo inserito manualmente: {price_text}")
        
        await update.message.reply_text(f"✅ Prezzo salvato: {price_text}")
        
        # Passa alla selezione categoria
        return await self.ask_category(update, context)

    async def handle_waiting_photos(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handler quando abbiamo chiesto una foto dopo scraping senza immagini"""
        message = update.message

        # Se manca il link nel contesto, chiedi di reinviare link + foto
        if not context.user_data.get('referral_link'):
            await message.reply_text(self.messages['need_media_and_link'])
            return ConversationHandler.END

        if not message.photo:
            await message.reply_text("⚠️ Inviami almeno una foto del prodotto (puoi aggiungere caption se vuoi).")
            return STATE_WAITING_PHOTOS

        photo = message.photo[-1]
        context.user_data.setdefault('photos', [])
        context.user_data['photos'].append(photo.file_id)

        await message.reply_text("✅ Foto ricevuta!\n\n✏️ Ora scrivi il nome del prodotto:")

        return STATE_WAITING_PRODUCT_NAME
    
    async def show_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Mostra l'anteprima dei post per tutti i canali
        Fase 3 del flusso
        """
        product_name = context.user_data.get('product_name', 'Prodotto')
        price = context.user_data.get('price', 'N/A')
        referral_link = context.user_data.get('referral_link', '')
        category = context.user_data.get('category', 'clothing')
        
        # Messaggio introduttivo
        preview_text = self.messages['preview_intro'] + "\n"
        
        # Genera anteprime per ogni canale
        for lang_code, channel_info in CHANNELS.items():
            preview_text += self.messages['preview_channel'].format(
                flag=channel_info['emoji_flag'],
                name=channel_info['name']
            )
            
            # Genera la caption per questa lingua
            caption = create_post_caption(
                product_name=product_name,
                price=price,
                referral_link=referral_link,
                category=category,
                language=lang_code
            )
            
            # Aggiungi l'anteprima (primi 200 caratteri)
            preview_text += f"```\n{caption[:200]}...\n```\n"
        
        # Invia l'anteprima
        if update.callback_query:
            await update.callback_query.message.reply_text(
                preview_text,
                parse_mode=ParseMode.MARKDOWN
            )
            target_message = update.callback_query.message
        else:
            target_message = await update.message.reply_text(
                preview_text,
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Chiedi conferma
        keyboard = [
            [
                InlineKeyboardButton(
                    self.messages['button_confirm'],
                    callback_data="confirm_publish"
                ),
                InlineKeyboardButton(
                    self.messages['button_cancel'],
                    callback_data="cancel_publish"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await target_message.reply_text(
            self.messages['confirm_publish'],
            reply_markup=reply_markup
        )
        
        return STATE_CONFIRM
    
    async def handle_publish_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handler per la conferma di pubblicazione
        Fase 4 del flusso - Pubblica sui canali
        """
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel_publish":
            await query.edit_message_text(self.messages['cancelled'])
            context.user_data.clear()
            return ConversationHandler.END
        
        # Conferma ricevuta, inizia la pubblicazione
        await query.edit_message_text(self.messages['publishing'])
        
        product_name = context.user_data.get('product_name', 'Prodotto')
        price = context.user_data.get('price', 'N/A')
        referral_link = context.user_data.get('referral_link', '')
        category = context.user_data.get('category', 'clothing')
        photos = context.user_data.get('photos', [])
        photos_are_urls = context.user_data.get('photos_are_urls', False)
        
        if not photos:
            await query.message.reply_text("❌ Nessuna foto trovata!")
            return ConversationHandler.END
        
        # Pubblica su ogni canale
        publish_results = []
        
        for lang_code, channel_info in CHANNELS.items():
            channel_id = channel_info['chat_id']
            channel_name = f"{channel_info['emoji_flag']} {channel_info['name']}"
            
            try:
                # Genera la caption per questa lingua
                caption = create_post_caption(
                    product_name=product_name,
                    price=price,
                    referral_link=referral_link,
                    category=category,
                    language=lang_code
                )
                
                # Prepara il media group con file aperti
                media_group = []
                files_to_close = []
                
                try:
                    for idx, photo_id in enumerate(photos):
                        if idx == 0:
                            # Prima foto con caption
                            if photos_are_urls or photo_id.startswith('/') or photo_id.startswith('\\') or os.path.exists(photo_id):
                                # Se è un file locale, aprilo e tienilo aperto
                                f = open(photo_id, 'rb')
                                files_to_close.append(f)
                                media_group.append(
                                    InputMediaPhoto(
                                        media=f,
                                        caption=caption,
                                        parse_mode=ParseMode.MARKDOWN
                                    )
                                )
                            else:
                                # Se è file_id dell'utente
                                media_group.append(
                                    InputMediaPhoto(
                                        media=photo_id,
                                        caption=caption,
                                        parse_mode=ParseMode.MARKDOWN
                                    )
                                )
                        else:
                            # Altre foto senza caption
                            if photos_are_urls or photo_id.startswith('/') or photo_id.startswith('\\') or os.path.exists(photo_id):
                                f = open(photo_id, 'rb')
                                files_to_close.append(f)
                                media_group.append(InputMediaPhoto(media=f))
                            else:
                                media_group.append(InputMediaPhoto(media=photo_id))
                
                    # Invia il media group al canale
                    await context.bot.send_media_group(
                        chat_id=channel_id,
                        media=media_group
                    )
                finally:
                    # Chiudi tutti i file aperti
                    for f in files_to_close:
                        f.close()
                
                publish_results.append({
                    'channel': channel_name,
                    'success': True
                })
                
                logger.info(f"Post pubblicato con successo su {channel_name}")
                
                await query.message.reply_text(
                    self.messages['publish_success'].format(channel=channel_name)
                )
                
            except Exception as e:
                logger.error(f"Errore nella pubblicazione su {channel_name}: {e}")
                publish_results.append({
                    'channel': channel_name,
                    'success': False,
                    'error': str(e)
                })
                
                await query.message.reply_text(
                    self.messages['publish_error'].format(
                        channel=channel_name,
                        error=str(e)
                    )
                )
        
        # Riepilogo finale
        summary = "\n".join([
            f"{'✅' if r['success'] else '❌'} {r['channel']}"
            for r in publish_results
        ])
        
        await query.message.reply_text(
            self.messages['publish_complete'].format(summary=summary)
        )
        
        # Pulisci i dati utente
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handler per il comando /cancel"""
        await update.message.reply_text(self.messages['cancelled'])
        context.user_data.clear()
        return ConversationHandler.END
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler globale per gli errori"""
        logger.error(f"Errore: {context.error}", exc_info=context.error)
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                self.messages['error_generic'].format(error=str(context.error))
            )


def main():
    """Funzione principale per avviare il bot"""
    
    # Verifica che il token sia configurato
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("⚠️ BOT_TOKEN non configurato! Modifica il file .env o config.py")
        return
    
    if ADMIN_USER_ID == 0:
        logger.error("⚠️ ADMIN_USER_ID non configurato! Modifica il file .env o config.py")
        return
    
    # Crea l'istanza del bot
    bot = AffiliateBot()
    
    # Crea l'applicazione
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Definisci il ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                (filters.PHOTO | filters.TEXT) & filters.User(user_id=ADMIN_USER_ID),
                bot.handle_media_group
            )
        ],
        states={
            STATE_WAITING_PRODUCT_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & filters.User(user_id=ADMIN_USER_ID),
                    bot.handle_product_name
                )
            ],
            STATE_WAITING_CATEGORY: [
                CallbackQueryHandler(
                    bot.handle_category_selection,
                    pattern=r'^cat_'
                )
            ],
            STATE_WAITING_PRICE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & filters.User(user_id=ADMIN_USER_ID),
                    bot.handle_manual_price
                )
            ],
            STATE_WAITING_PHOTOS: [
                MessageHandler(
                    filters.PHOTO & filters.User(user_id=ADMIN_USER_ID),
                    bot.handle_waiting_photos
                )
            ],
            STATE_CONFIRM: [
                CallbackQueryHandler(
                    bot.handle_publish_confirmation,
                    pattern=r'^(confirm|cancel)_publish$'
                )
            ],
        },
        fallbacks=[
            CommandHandler('cancel', bot.cancel, filters=filters.User(user_id=ADMIN_USER_ID))
        ],
    )
    
    # Aggiungi gli handlers
    application.add_handler(CommandHandler('start', bot.start))
    application.add_handler(conv_handler)
    
    # Aggiungi error handler
    application.add_error_handler(bot.error_handler)
    
    # Avvia il bot
    logger.info(SYSTEM_MESSAGES['start_bot'])
    print("\n" + "="*50)
    print("🤖 BOT AVVIATO CON SUCCESSO!")
    print("="*50)
    print(f"📱 Admin User ID: {ADMIN_USER_ID}")
    print(f"🌍 Canali configurati: {len(CHANNELS)}")
    print(f"📂 Categorie disponibili: {len(CATEGORIES)}")
    print("="*50 + "\n")
    
    # Polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
