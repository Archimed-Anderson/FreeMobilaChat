"""
Documentation Scraper for FreeMobilaChat SAV Knowledge Base
Scrapes Free Mobile assistance documentation and creates embeddings for semantic search
"""

import asyncio
import hashlib
import logging
import re
from datetime import datetime, UTC
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse
import json

# Web scraping imports
try:
    import requests
    from bs4 import BeautifulSoup
    import aiohttp
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("Web scraping dependencies not available. Install: pip install requests beautifulsoup4 aiohttp")

# Embeddings imports
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Embeddings dependencies not available. Install: pip install sentence-transformers")

from ..models import KnowledgeDocument, DocumentType
from ..utils.database import DatabaseManager

logger = logging.getLogger(__name__)

class DocumentationScraper:
    """Service pour scraper et indexer la documentation Free Mobile"""
    
    # URLs de base de la documentation Free Mobile
    BASE_URLS = [
        "https://assistance.free.fr/",
        "https://assistance.free.fr/univers/mobile-free/",
        "https://assistance.free.fr/univers/mobile-free/mon-mobile/premiers-pas",
        "https://assistance.free.fr/articles/achat-de-telephone-garanties-legales-et-service-apres-vente-965"
    ]
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialiser le scraper de documentation
        
        Args:
            db_manager: Gestionnaire de base de données
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Vérifier les dépendances (mode dégradé si non disponibles)
        if not SCRAPING_AVAILABLE:
            self.logger.warning(" Web scraping dependencies not available. Scraping will be disabled.")

        if not EMBEDDINGS_AVAILABLE:
            self.logger.warning(" Embeddings dependencies not available. Semantic search will be disabled.")
        
        # Initialiser le modèle d'embeddings (modèle français optimisé)
        self.embedding_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        self.embedding_model = None
        self._initialize_embedding_model()
        
        # Configuration du scraping
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Cache pour éviter de scraper les mêmes pages
        self.scraped_urls = set()
        self.failed_urls = set()
    
    def _initialize_embedding_model(self):
        """Initialiser le modèle d'embeddings"""
        if not EMBEDDINGS_AVAILABLE:
            self.logger.warning(" Modèle d'embeddings non disponible (dépendances manquantes)")
            self.embedding_model = None
            return

        try:
            self.logger.info(f"🤖 Initialisation du modèle d'embeddings: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.logger.info(" Modèle d'embeddings initialisé avec succès")
        except Exception as e:
            self.logger.error(f" Erreur lors de l'initialisation du modèle d'embeddings: {e}")
            self.embedding_model = None
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoyer et normaliser le texte extrait
        
        Args:
            text: Texte brut à nettoyer
            
        Returns:
            Texte nettoyé
        """
        if not text:
            return ""
        
        # Supprimer les espaces multiples et les retours à la ligne
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Supprimer les espaces en début et fin
        text = text.strip()
        
        return text
    
    def _extract_content_from_html(self, html: str, url: str) -> Tuple[str, str, DocumentType]:
        """
        Extraire le contenu principal d'une page HTML
        
        Args:
            html: Code HTML de la page
            url: URL de la page
            
        Returns:
            Tuple (titre, contenu, type_document)
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Supprimer les scripts, styles et autres éléments non pertinents
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Extraire le titre
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = self._clean_text(title_tag.get_text())
            
            # Si pas de titre dans <title>, chercher dans h1
            if not title:
                h1_tag = soup.find('h1')
                if h1_tag:
                    title = self._clean_text(h1_tag.get_text())
            
            # Extraire le contenu principal
            content_selectors = [
                'main',
                '.content',
                '.main-content',
                '.article-content',
                '.page-content',
                'article',
                '.container'
            ]
            
            content = ""
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    content = self._clean_text(content_element.get_text())
                    break
            
            # Si aucun sélecteur spécifique trouvé, prendre le body
            if not content:
                body = soup.find('body')
                if body:
                    content = self._clean_text(body.get_text())
            
            # Déterminer le type de document basé sur l'URL et le contenu
            document_type = self._determine_document_type(url, title, content)
            
            return title, content, document_type
            
        except Exception as e:
            self.logger.error(f" Erreur lors de l'extraction du contenu de {url}: {e}")
            return "", "", DocumentType.GENERAL
    
    def _determine_document_type(self, url: str, title: str, content: str) -> DocumentType:
        """
        Déterminer le type de document basé sur l'URL et le contenu
        
        Args:
            url: URL du document
            title: Titre du document
            content: Contenu du document
            
        Returns:
            Type de document
        """
        url_lower = url.lower()
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Mots-clés pour chaque type
        faq_keywords = ['faq', 'questions', 'réponses', 'comment', 'pourquoi']
        guide_keywords = ['guide', 'tutoriel', 'étapes', 'procédure', 'premiers pas']
        troubleshooting_keywords = ['problème', 'panne', 'erreur', 'dépannage', 'résoudre', 'solution']
        procedure_keywords = ['configuration', 'paramétrage', 'installation', 'activation']
        
        # Vérifier dans l'URL d'abord
        if any(keyword in url_lower for keyword in faq_keywords):
            return DocumentType.FAQ
        if any(keyword in url_lower for keyword in guide_keywords):
            return DocumentType.GUIDE
        if any(keyword in url_lower for keyword in troubleshooting_keywords):
            return DocumentType.TROUBLESHOOTING
        if any(keyword in url_lower for keyword in procedure_keywords):
            return DocumentType.PROCEDURE
        
        # Vérifier dans le titre
        if any(keyword in title_lower for keyword in faq_keywords):
            return DocumentType.FAQ
        if any(keyword in title_lower for keyword in guide_keywords):
            return DocumentType.GUIDE
        if any(keyword in title_lower for keyword in troubleshooting_keywords):
            return DocumentType.TROUBLESHOOTING
        if any(keyword in title_lower for keyword in procedure_keywords):
            return DocumentType.PROCEDURE
        
        # Vérifier dans le contenu (échantillon)
        content_sample = content_lower[:1000]  # Premier 1000 caractères
        if any(keyword in content_sample for keyword in faq_keywords):
            return DocumentType.FAQ
        if any(keyword in content_sample for keyword in guide_keywords):
            return DocumentType.GUIDE
        if any(keyword in content_sample for keyword in troubleshooting_keywords):
            return DocumentType.TROUBLESHOOTING
        if any(keyword in content_sample for keyword in procedure_keywords):
            return DocumentType.PROCEDURE
        
        return DocumentType.GENERAL
    
    def _generate_content_hash(self, content: str) -> str:
        """
        Générer un hash SHA-256 du contenu pour détecter les changements
        
        Args:
            content: Contenu à hasher
            
        Returns:
            Hash SHA-256 en hexadécimal
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _generate_embeddings(self, text: str) -> Optional[List[float]]:
        """
        Générer les embeddings pour un texte
        
        Args:
            text: Texte à encoder
            
        Returns:
            Vecteur d'embeddings ou None si erreur
        """
        try:
            if not self.embedding_model:
                self.logger.error(" Modèle d'embeddings non initialisé")
                return None
            
            # Limiter la taille du texte pour éviter les erreurs de mémoire
            max_length = 512  # Limite du modèle
            if len(text) > max_length:
                text = text[:max_length]
            
            embeddings = self.embedding_model.encode(text, convert_to_tensor=False)
            return embeddings.tolist()
            
        except Exception as e:
            self.logger.error(f" Erreur lors de la génération des embeddings: {e}")
            return None

    async def scrape_url(self, url: str) -> Optional[KnowledgeDocument]:
        """
        Scraper une URL et créer un document de connaissances

        Args:
            url: URL à scraper

        Returns:
            Document de connaissances ou None si erreur
        """
        if url in self.scraped_urls or url in self.failed_urls:
            self.logger.info(f"URL already processed: {url}")
            return None

        try:
            self.logger.info(f"Scraping URL: {url}")

            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        self.logger.warning(f" Statut HTTP {response.status} pour {url}")
                        self.failed_urls.add(url)
                        return None

                    html = await response.text()

            # Extraire le contenu
            title, content, document_type = self._extract_content_from_html(html, url)

            if not content or len(content) < 50:
                self.logger.warning(f" Contenu insuffisant pour {url}")
                self.failed_urls.add(url)
                return None

            # Générer le hash du contenu
            content_hash = self._generate_content_hash(content)

            # Générer les embeddings
            embeddings = self._generate_embeddings(content)
            if not embeddings:
                self.logger.warning(f" Impossible de générer les embeddings pour {url}")

            # Extraire le domaine
            parsed_url = urlparse(url)
            source_domain = parsed_url.netloc

            # Créer le document
            document = KnowledgeDocument(
                title=title or f"Document de {source_domain}",
                content=content,
                document_type=document_type,
                source_url=url,
                source_domain=source_domain,
                content_hash=content_hash,
                embedding_model=self.embedding_model_name if embeddings else None,
                embedding_dimension=len(embeddings) if embeddings else None
            )

            self.scraped_urls.add(url)
            self.logger.info(f" Document créé: {title[:50]}... ({len(content)} caractères)")

            return document

        except Exception as e:
            self.logger.error(f" Erreur lors du scraping de {url}: {e}")
            self.failed_urls.add(url)
            return None

    async def scrape_all_documentation(self) -> List[KnowledgeDocument]:
        """
        Scraper toute la documentation Free Mobile

        Returns:
            Liste des documents créés
        """
        self.logger.info(" Début du scraping de la documentation Free Mobile")

        documents = []

        # Scraper les URLs de base
        for url in self.BASE_URLS:
            document = await self.scrape_url(url)
            if document:
                documents.append(document)

            # Pause entre les requêtes pour être respectueux
            await asyncio.sleep(1)

        self.logger.info(f" Scraping terminé: {len(documents)} documents créés")
        self.logger.info(f" URLs échouées: {len(self.failed_urls)}")

        return documents

    async def store_documents(self, documents: List[KnowledgeDocument]) -> int:
        """
        Stocker les documents dans la base de données

        Args:
            documents: Liste des documents à stocker

        Returns:
            Nombre de documents stockés
        """
        if not self.db_manager:
            self.logger.error(" Gestionnaire de base de données non disponible")
            return 0

        stored_count = 0

        for document in documents:
            try:
                # Vérifier si le document existe déjà (par hash de contenu)
                existing = await self._check_existing_document(document.content_hash)

                if existing:
                    self.logger.info(f"Document already exists: {document.title[:50]}...")
                    continue

                # Stocker le document
                await self._store_single_document(document)
                stored_count += 1
                self.logger.info(f"Document stored: {document.title[:50]}...")

            except Exception as e:
                self.logger.error(f" Erreur lors du stockage de {document.title[:50]}...: {e}")

        self.logger.info(f" Stockage terminé: {stored_count} nouveaux documents")
        return stored_count

    async def _check_existing_document(self, content_hash: str) -> bool:
        """
        Vérifier si un document existe déjà par son hash

        Args:
            content_hash: Hash du contenu à vérifier

        Returns:
            True si le document existe déjà
        """
        try:
            # Cette méthode devra être implémentée selon le système de base de données
            # Pour l'instant, on retourne False (pas de vérification)
            return False
        except Exception as e:
            self.logger.error(f" Erreur lors de la vérification d'existence: {e}")
            return False

    async def _store_single_document(self, document: KnowledgeDocument):
        """
        Stocker un seul document dans la base de données

        Args:
            document: Document à stocker
        """
        try:
            # Cette méthode devra être implémentée selon le système de base de données
            # Pour l'instant, on log juste les informations
            self.logger.info(f" Stockage du document: {document.title}")
            self.logger.debug(f"   - URL: {document.source_url}")
            self.logger.debug(f"   - Type: {document.document_type}")
            self.logger.debug(f"   - Taille: {len(document.content)} caractères")
            self.logger.debug(f"   - Hash: {document.content_hash}")

        except Exception as e:
            self.logger.error(f" Erreur lors du stockage: {e}")
            raise

    async def update_knowledge_base(self) -> Dict[str, Any]:
        """
        Mettre à jour complètement la base de connaissances

        Returns:
            Résumé de l'opération
        """
        start_time = datetime.now(UTC)
        self.logger.info("🔄 Début de la mise à jour de la base de connaissances")

        try:
            # Scraper tous les documents
            documents = await self.scrape_all_documentation()

            # Stocker les documents
            stored_count = await self.store_documents(documents)

            end_time = datetime.now(UTC)
            duration = (end_time - start_time).total_seconds()

            result = {
                'success': True,
                'start_time': start_time,
                'end_time': end_time,
                'duration_seconds': duration,
                'total_urls_processed': len(self.scraped_urls) + len(self.failed_urls),
                'successful_scrapes': len(documents),
                'failed_scrapes': len(self.failed_urls),
                'documents_stored': stored_count,
                'failed_urls': list(self.failed_urls)
            }

            self.logger.info(f" Mise à jour terminée en {duration:.1f}s")
            self.logger.info(f" Résumé: {len(documents)} documents scrapés, {stored_count} stockés")

            return result

        except Exception as e:
            self.logger.error(f" Erreur lors de la mise à jour: {e}")
            return {
                'success': False,
                'error': str(e),
                'start_time': start_time,
                'end_time': datetime.now(UTC)
            }
