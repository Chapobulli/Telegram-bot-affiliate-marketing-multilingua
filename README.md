# 🤖 Telegram Bot per Affiliate Marketing - Fashion

Bot Telegram multilingua professionale per pubblicare prodotti di abbigliamento (Oopbuy/Weidian) su diversi canali con scraping automatico dei prezzi.

## 📋 Caratteristiche

- ✅ **Web Scraping Automatico**: Estrae prezzi e nomi prodotti da Oopbuy/Weidian usando Selenium
- 🌍 **Multilingua**: Supporto per Italiano, Inglese e Spagnolo
- 📱 **Multi-Canale**: Pubblica automaticamente su più canali Telegram
- 🔒 **Sicurezza**: Protetto da filtro User ID
- 📝 **Template Professionali**: Post accattivanti con emoji e hyperlink nascosti
- 🎯 **Categorie**: Sistema di categorizzazione prodotti con hashtag
- 📸 **Media Group**: Supporto completo per album di foto
- 🔄 **Fallback Manuale**: Se lo scraping fallisce, permette inserimento manuale

## 🚀 Setup Iniziale

### 1. Prerequisiti

- Python 3.8 o superiore
- Google Chrome installato
- Account Telegram con bot creato (@BotFather)

### 2. Installazione

#### Windows

```powershell
# Crea e attiva virtual environment
python -m venv venv
.\venv\Scripts\activate

# Installa le dipendenze
pip install -r requirements.txt
```

#### Linux/Mac

```bash
# Crea e attiva virtual environment
python3 -m venv venv
source venv/bin/activate

# Installa le dipendenze
pip install -r requirements.txt
```

### 3. Configurazione

#### A. Crea il file .env

Crea un file chiamato `.env` nella root del progetto:

```env
# Token del bot (da @BotFather)
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Il tuo User ID Telegram (scoprilo con @userinfobot)
ADMIN_USER_ID=123456789

# Canali Telegram (username o chat_id)
CHANNEL_IT=@tuocanale_italiano
CHANNEL_EN=@tuocanale_english
CHANNEL_ES=@tuocanale_espanol
```

#### B. Ottieni il tuo User ID

1. Apri Telegram
2. Cerca il bot [@userinfobot](https://t.me/userinfobot)
3. Avvialo con `/start`
4. Copia il tuo User ID

#### C. Crea il bot Telegram

1. Apri Telegram e cerca [@BotFather](https://t.me/BotFather)
2. Invia `/newbot`
3. Segui le istruzioni per creare il bot
4. Copia il **Token** che ti viene fornito
5. Incollalo nel file `.env`

#### D. Configura i canali

Per ogni canale:
1. Crea un canale Telegram
2. Aggiungi il bot come amministratore con permessi di pubblicazione
3. Usa il nome utente del canale (es. `@miocanale`) o il chat_id nel file `.env`

### 4. Configurazione Chrome/ChromeDriver

Il bot usa **webdriver-manager** che scarica automaticamente ChromeDriver. Devi solo avere Chrome installato:

#### Windows
- Scarica [Google Chrome](https://www.google.com/chrome/) se non lo hai già
- ChromeDriver verrà scaricato automaticamente al primo avvio

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# O usa Chrome ufficiale
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

#### Mac
```bash
# Con Homebrew
brew install --cask google-chrome
```

### 5. Avvio del Bot

```powershell
# Con virtual environment attivo
python bot.py
```

Se tutto è configurato correttamente, vedrai:

```
==================================================
🤖 BOT AVVIATO CON SUCCESSO!
==================================================
📱 Admin User ID: 123456789
🌍 Canali configurati: 3
📂 Categorie disponibili: 5
==================================================
```

## 📖 Come Usare il Bot

### Flusso di Lavoro

1. **Invia le foto**
   - Seleziona 2-10 foto del prodotto
   - Nella caption, incolla il link con il tuo inviteCode
   - Invia come gruppo di foto (Media Group)

2. **Scraping Automatico**
   - Il bot estrae automaticamente prezzo e nome prodotto
   - Se fallisce, ti chiederà di inserire il prezzo manualmente

3. **Selezione Categoria**
   - Scegli la categoria appropriata dai pulsanti
   - Esempi: 👟 Scarpe, 👕 Abbigliamento, 👜 Accessori

4. **Anteprima**
   - Visualizza come apparirà il post in ogni lingua
   - Controlla che tutto sia corretto

5. **Pubblicazione**
   - Conferma per pubblicare su tutti i canali
   - Ricevi conferma per ogni canale

### Esempio Pratico

```
1. Seleziona 3 foto di Nike Air Jordan
2. Nella caption scrivi:
   https://www.oopbuy.com/product/?url=https://weidian.com/item.html?itemID=4480454092&inviteCode=ABC123

3. Invia al bot
4. Il bot estrae: "Nike Air Jordan 1 High - ¥399"
5. Scegli categoria: 👟 Scarpe
6. Conferma l'anteprima
7. ✅ Pubblicato su 3 canali!
```

## 🎨 Personalizzazione

### Aggiungere Nuove Lingue

Modifica [config.py](config.py):

```python
CHANNELS = {
    'IT': {...},
    'EN': {...},
    'FR': {  # Nuovo!
        'chat_id': '@canale_francese',
        'name': 'Français',
        'emoji_flag': '🇫🇷'
    }
}
```

Aggiungi i template in [templates.py](templates.py).

### Aggiungere Nuove Categorie

Modifica [config.py](config.py):

```python
CATEGORIES = {
    # ... categorie esistenti ...
    'jewelry': {
        'IT': {'name': 'Gioielli', 'hashtag': '#GIOIELLI', 'emoji': '💎'},
        'EN': {'name': 'Jewelry', 'hashtag': '#JEWELRY', 'emoji': '💎'},
        'ES': {'name': 'Joyería', 'hashtag': '#JOYERIA', 'emoji': '💎'}
    }
}
```

### Modificare i Template

Modifica la funzione `create_post_caption` in [templates.py](templates.py) per personalizzare il formato dei post.

## 🔧 Risoluzione Problemi

### Il bot non risponde
- Verifica che `ADMIN_USER_ID` sia corretto
- Controlla che il bot sia avviato
- Verifica la connessione internet

### Scraping fallisce sempre
- Chrome potrebbe non essere installato
- Il sito potrebbe aver cambiato struttura
- Inserisci il prezzo manualmente quando richiesto

### Errore di pubblicazione su un canale
- Verifica che il bot sia admin del canale
- Controlla che il `chat_id` sia corretto
- Il canale deve essere pubblico o il bot deve essere membro

### ChromeDriver non funziona
```bash
# Reinstalla webdriver-manager
pip uninstall webdriver-manager
pip install webdriver-manager --upgrade

# O scarica manualmente ChromeDriver
# https://chromedriver.chromium.org/downloads
```

### ImportError o ModuleNotFoundError
```bash
# Assicurati che il venv sia attivo
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstalla le dipendenze
pip install -r requirements.txt
```

## 📁 Struttura del Progetto

```
telegrambot-refferal-fashion/
├── bot.py              # File principale del bot
├── config.py           # Configurazioni e costanti
├── scraper.py          # Modulo web scraping
├── templates.py        # Template multilingua
├── requirements.txt    # Dipendenze Python
├── .env               # Variabili d'ambiente (da creare)
└── README.md          # Questa documentazione
```

## 🔒 Sicurezza

- ✅ **Solo tu** puoi usare il bot (filtro User ID)
- ✅ Token e credenziali in `.env` (non committare!)
- ✅ Logging completo per debugging
- ✅ Gestione errori robusta

### Aggiungi .env al .gitignore

Se usi Git, crea un file `.gitignore`:

```
# Virtual environment
venv/
__pycache__/
*.pyc

# Configurazioni sensibili
.env

# Log files
*.log

# IDE
.vscode/
.idea/
```

## 📝 Logging

Il bot registra tutte le operazioni:
- ✅ Tentativi di accesso
- 🔍 Risultati scraping
- 📤 Pubblicazioni su canali
- ❌ Errori e eccezioni

I log appariranno nella console durante l'esecuzione.

## 🆘 Supporto

### Comandi Disponibili

- `/start` - Avvia il bot e mostra il messaggio di benvenuto
- `/cancel` - Annulla l'operazione corrente

### Test dello Scraper

Puoi testare lo scraper indipendentemente:

```python
python scraper.py
```

### Test dei Template

```python
python templates.py
```

## 🎯 Feature Avanzate

### Hyperlink Nascosti

Il bot usa automaticamente hyperlink nascosti per rendere i post più puliti:

❌ Prima:
```
https://www.oopbuy.com/product/?url=https://weidian.com/item.html?itemID=4480454092&inviteCode=ABC123DEFG456
```

✅ Dopo:
```
👉 [CLICCA QUI PER ACQUISTARE]
```

### Gestione Media Group

Il bot gestisce correttamente gruppi di foto:
- Prima foto: con caption completa
- Altre foto: senza caption (più pulito)

### Fallback Manuale

Se lo scraping fallisce:
1. Il bot ti avvisa
2. Puoi inserire il prezzo manualmente
3. Il flusso continua normalmente

## 📊 Statistiche

Per tracciare le performance, considera di aggiungere:
- Database per salvare i post pubblicati
- Analytics sui click (tramite short URL)
- Report automatici delle pubblicazioni

## 🔄 Aggiornamenti

Per aggiornare il bot:

```bash
# Attiva venv
.\venv\Scripts\activate

# Aggiorna dipendenze
pip install -r requirements.txt --upgrade

# Riavvia il bot
python bot.py
```

## 📜 Licenza

Questo progetto è per uso personale. Assicurati di rispettare i termini di servizio di:
- Telegram
- Oopbuy
- Weidian
- Qualsiasi altro servizio utilizzato

## 👨‍💻 Sviluppo

Il codice è commentato e strutturato per facilitare le modifiche:
- **bot.py**: Logica principale e ConversationHandler
- **scraper.py**: Logica di scraping (facilmente estendibile)
- **templates.py**: Template messaggi (semplice da personalizzare)
- **config.py**: Tutte le configurazioni in un posto

---

**Buon affiliate marketing! 🚀💰**
