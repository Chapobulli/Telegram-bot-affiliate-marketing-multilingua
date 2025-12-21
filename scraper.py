"""
Modulo per Web Scraping di Oopbuy e Weidian
Estrae informazioni sui prodotti (prezzo e nome) da link di affiliazione
"""

import logging
import time
import requests
import os
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from config import SCRAPING_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)


class ProductScraper:
    """
    Classe per lo scraping di prodotti da vari siti di e-commerce
    """
    
    def __init__(self):
        """Inizializza il browser Selenium in modalità headless"""
        self.driver = None
        self.images_cache_dir = "downloaded_images"
        if not os.path.exists(self.images_cache_dir):
            os.makedirs(self.images_cache_dir)
        
    def _init_driver(self):
        """Inizializza il driver Chrome in modalità headless"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Modalità senza interfaccia grafica
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'user-agent={USER_AGENT}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Usa webdriver-manager per gestire automaticamente ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Driver Chrome inizializzato con successo in modalità headless")
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione del driver: {e}")
            return False
    
    def _close_driver(self):
        """Chiude il driver se è aperto"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver Chrome chiuso correttamente")
            except Exception as e:
                logger.error(f"Errore nella chiusura del driver: {e}")
            finally:
                self.driver = None
    
    def _download_images(self, image_urls: List[str]) -> List[str]:
        """Scarica le immagini localmente e restituisce i percorsi"""
        downloaded_paths = []
        
        for idx, img_url in enumerate(image_urls):
            try:
                if not img_url or not img_url.startswith('http'):
                    continue
                
                # Scarica l'immagine
                response = requests.get(img_url, timeout=10, headers={'User-Agent': USER_AGENT})
                response.raise_for_status()
                
                # Salva localmente
                ext = img_url.split('.')[-1].split('?')[0][:4]  # jpg, png, etc
                if ext not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                    ext = 'jpg'
                
                filename = os.path.join(self.images_cache_dir, f"product_{int(time.time())}_{idx}.{ext}")
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                downloaded_paths.append(filename)
                logger.info(f"Immagine scaricata: {filename}")
                
            except Exception as e:
                logger.warning(f"Impossibile scaricare {img_url}: {e}")
                continue
        
        return downloaded_paths
    
    def scrape_oopbuy(self, url: str) -> Dict[str, Optional[str]]:
        """
        Estrae il prezzo e il nome del prodotto da Oopbuy
        
        Args:
            url: Link del prodotto Oopbuy
            
        Returns:
            Dizionario con 'price', 'product_name', e 'success'
        """
        result = {
            'price': None,
            'product_name': None,
            'images': [],
            'success': False,
            'error': None
        }
        
        try:
            logger.info(f"Avvio scraping Oopbuy: {url[:50]}...")
            
            # Inizializza il driver
            if not self._init_driver():
                result['error'] = "Impossibile inizializzare il browser"
                return result
            
            # Carica la pagina
            self.driver.get(url)
            logger.info("Pagina caricata, attendo il caricamento dinamico...")
            
            # Attendi che il prezzo venga caricato (Oopbuy usa caricamento dinamico)
            # Prova diversi selettori comuni per il prezzo
            price_selectors = [
                "//span[contains(@class, 'price')]",
                "//div[contains(@class, 'price')]",
                "//*[contains(text(), '¥') or contains(text(), '$') or contains(text(), '€')]",
                "//span[contains(@class, 'amount')]",
                "//*[@class='product-price']"
            ]
            
            price = None
            for selector in price_selectors:
                try:
                    element = WebDriverWait(self.driver, SCRAPING_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    price_text = element.text.strip()
                    if price_text and any(c.isdigit() for c in price_text):
                        price = price_text
                        logger.info(f"Prezzo trovato: {price}")
                        break
                except TimeoutException:
                    continue
            
            # Estrai il nome del prodotto
            product_name = None
            title_selectors = [
                "//h1",
                "//title",
                "//*[contains(@class, 'product-title')]",
                "//*[contains(@class, 'product-name')]",
                "//h2"
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    name_text = element.text.strip()
                    if name_text and len(name_text) > 3:
                        product_name = name_text
                        logger.info(f"Nome prodotto trovato: {product_name[:50]}...")
                        break
                except NoSuchElementException:
                    continue
            
            # Se non abbiamo trovato il nome, usa il title della pagina
            if not product_name:
                try:
                    product_name = self.driver.title.strip()
                except:
                    product_name = "Prodotto"

            # NON scaricare immagini (l'utente le invierà manualmente)
            result['images'] = []
            
            if price:
                result['price'] = price
                result['product_name'] = product_name
                result['success'] = True
                logger.info("Scraping completato con successo!")
            else:
                result['error'] = "Prezzo non trovato sulla pagina"
                logger.warning("Impossibile estrarre il prezzo dalla pagina")
                
        except TimeoutException:
            result['error'] = f"Timeout: la pagina non si è caricata entro {SCRAPING_TIMEOUT} secondi"
            logger.error(result['error'])
            
        except Exception as e:
            result['error'] = f"Errore durante lo scraping: {str(e)}"
            logger.error(result['error'], exc_info=True)
            
        finally:
            self._close_driver()
        
        return result
    
    def scrape_weidian(self, url: str) -> Dict[str, Optional[str]]:
        """
        Estrae il prezzo e il nome del prodotto da Weidian
        
        Args:
            url: Link del prodotto Weidian
            
        Returns:
            Dizionario con 'price', 'product_name', e 'success'
        """
        result = {
            'price': None,
            'product_name': None,
            'images': [],
            'success': False,
            'error': None
        }
        
        try:
            logger.info(f"Avvio scraping Weidian: {url[:50]}...")
            
            if not self._init_driver():
                result['error'] = "Impossibile inizializzare il browser"
                return result
            
            self.driver.get(url)
            logger.info("Pagina caricata, attendo il caricamento dinamico...")
            
            # Attendi caricamento
            time.sleep(3)
            
            # Selettori specifici per Weidian
            price_selectors = [
                "//span[contains(@class, 'price')]",
                "//*[contains(text(), '¥')]",
                "//div[@class='product-price']"
            ]
            
            price = None
            for selector in price_selectors:
                try:
                    element = WebDriverWait(self.driver, SCRAPING_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    price_text = element.text.strip()
                    if price_text and any(c.isdigit() for c in price_text):
                        price = price_text
                        break
                except:
                    continue
            
            # Nome prodotto
            product_name = None
            try:
                element = self.driver.find_element(By.TAG_NAME, "h1")
                product_name = element.text.strip()
            except:
                product_name = self.driver.title.strip()
            
            # NON scaricare immagini (l'utente le invierà manualmente)
            result['images'] = []

            if price:
                result['price'] = price
                result['product_name'] = product_name
                result['success'] = True
                logger.info("Scraping Weidian completato con successo!")
            else:
                result['error'] = "Prezzo non trovato"
                logger.warning("Impossibile estrarre il prezzo da Weidian")
                
        except Exception as e:
            result['error'] = f"Errore: {str(e)}"
            logger.error(result['error'], exc_info=True)
            
        finally:
            self._close_driver()
        
        return result
    
    def scrape_product(self, url: str) -> Dict[str, Optional[str]]:
        """
        Determina automaticamente il sito e fa lo scraping appropriato
        
        Args:
            url: Link del prodotto
            
        Returns:
            Dizionario con i dati estratti
        """
        url_lower = url.lower()
        
        if 'oopbuy' in url_lower:
            return self.scrape_oopbuy(url)
        elif 'weidian' in url_lower:
            return self.scrape_weidian(url)
        else:
            # Prova lo scraping generico con Oopbuy come fallback
            logger.warning(f"Sito non riconosciuto, provo scraping generico: {url[:50]}")
            return self.scrape_oopbuy(url)


def test_scraper():
    """Funzione di test per lo scraper"""
    scraper = ProductScraper()
    
    # Test URL (sostituisci con un URL reale per testare)
    test_url = "https://www.oopbuy.com/product/?url=example"
    
    result = scraper.scrape_product(test_url)
    
    print("\n=== RISULTATO SCRAPING ===")
    print(f"Success: {result['success']}")
    print(f"Prodotto: {result['product_name']}")
    print(f"Prezzo: {result['price']}")
    print(f"Immagini: {len(result.get('images', []))}")
    if result['error']:
        print(f"Errore: {result['error']}")
    print("========================\n")


if __name__ == "__main__":
    # Configura logging per test
    logging.basicConfig(level=logging.INFO)
    test_scraper()
