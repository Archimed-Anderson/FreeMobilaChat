"""
Tests unitaires pour le module text_cleaning
Validation de la robustesse NLP avec cas limites
"""

import pytest
from src.core.NLP_processing.text_cleaning import TextCleaner


class TestTextCleaner:
    """Tests pour la classe TextCleaner"""
    
    @pytest.fixture
    def cleaner(self):
        """Fixture pour instancier un TextCleaner"""
        return TextCleaner()
    
    def test_initialization(self, cleaner):
        """Teste l'initialisation correcte du cleaner"""
        assert cleaner is not None
        assert hasattr(cleaner, 'url_pattern')
        assert hasattr(cleaner, 'emoji_pattern')
        assert len(cleaner.french_stopwords) > 0


class TestCleanBasic:
    """Tests pour clean_basic"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_empty_text(self, cleaner):
        """Teste avec texte vide"""
        assert cleaner.clean_basic("") == ""
        assert cleaner.clean_basic(None) == ""
    
    def test_html_entities(self, cleaner):
        """Teste le décodage des entités HTML"""
        text = "Hello&nbsp;World&amp;test"
        result = cleaner.clean_basic(text)
        assert "&nbsp;" not in result
        assert "&amp;" not in result
        assert "Hello World&test" == result
    
    def test_whitespace_normalization(self, cleaner):
        """Teste la normalisation des espaces"""
        text = "Hello   \n\t  World"
        result = cleaner.clean_basic(text)
        assert result == "Hello World"
    
    def test_control_characters(self, cleaner):
        """Teste la suppression des caractères de contrôle"""
        text = "Hello\x00\x01World"
        result = cleaner.clean_basic(text)
        assert "\x00" not in result
        assert "\x01" not in result
    
    def test_unicode_text(self, cleaner):
        """Teste la gestion de l'Unicode"""
        text = "Café ☕ été 🌞"
        result = cleaner.clean_basic(text)
        assert "Café" in result
        assert "été" in result


class TestRemovalMethods:
    """Tests pour les méthodes de suppression"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_remove_urls(self, cleaner):
        """Teste la suppression d'URLs"""
        texts = [
            ("Check https://example.com now", "Check  now"),
            ("Visit www.site.com", "Visit "),
            ("No URL here", "No URL here")
        ]
        for input_text, expected in texts:
            result = cleaner.remove_urls(input_text)
            assert result == expected
    
    def test_remove_mentions(self, cleaner):
        """Teste la suppression de mentions"""
        text = "@user1 hello @user2"
        result = cleaner.remove_mentions(text)
        assert "@user1" not in result
        assert "@user2" not in result
        assert "hello" in result
    
    def test_remove_hashtags(self, cleaner):
        """Teste la suppression de hashtags"""
        text = "#python #code test"
        result = cleaner.remove_hashtags(text)
        assert "#python" not in result
        assert "#code" not in result
        assert "test" in result
    
    def test_remove_emojis(self, cleaner):
        """Teste la suppression d'emojis"""
        text = "Hello 😊 World 🌍"
        result = cleaner.remove_emojis(text)
        assert "😊" not in result
        assert "🌍" not in result
        assert "Hello" in result


class TestExtractionMethods:
    """Tests pour les méthodes d'extraction"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_extract_mentions(self, cleaner):
        """Teste l'extraction de mentions"""
        text = "@user1 hello @user2 and @user3"
        mentions = cleaner.extract_mentions(text)
        assert len(mentions) == 3
        assert "user1" in mentions
        assert "user2" in mentions
        assert "user3" in mentions
    
    def test_extract_hashtags(self, cleaner):
        """Teste l'extraction de hashtags"""
        text = "#python #nlp #testing"
        hashtags = cleaner.extract_hashtags(text)
        assert len(hashtags) == 3
        assert "python" in hashtags
        assert "nlp" in hashtags
    
    def test_extract_urls(self, cleaner):
        """Teste l'extraction d'URLs"""
        text = "Check https://site1.com and https://site2.com"
        urls = cleaner.extract_urls(text)
        assert len(urls) == 2
    
    def test_no_extraction(self, cleaner):
        """Teste l'extraction quand rien à extraire"""
        text = "Simple text without special elements"
        assert cleaner.extract_mentions(text) == []
        assert cleaner.extract_hashtags(text) == []
        assert cleaner.extract_urls(text) == []


class TestCleanForAnalysis:
    """Tests pour clean_for_analysis"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_basic_cleaning(self, cleaner):
        """Teste le nettoyage basique pour analyse"""
        text = "@Free le réseau est nul 😡 https://t.co/xxx"
        result = cleaner.clean_for_analysis(text, preserve_emojis=False)
        
        assert "https://" not in result
        assert "😡" not in result
        assert "@Free" in result  # Par défaut preserve_mentions=True
    
    def test_preserve_options(self, cleaner):
        """Teste les options de préservation"""
        text = "@user #hashtag emoji 😊 https://url.com"
        
        # Tout supprimer
        result = cleaner.clean_for_analysis(
            text,
            preserve_mentions=False,
            preserve_hashtags=False,
            preserve_emojis=False
        )
        assert "@user" not in result
        assert "#hashtag" not in result
        assert "😊" not in result
    
    def test_repeated_characters(self, cleaner):
        """Teste la normalisation des caractères répétés"""
        text = "noooooooon"
        result = cleaner.clean_for_analysis(text)
        # Devrait réduire à max 3 répétitions
        assert result == "nooon"
    
    @pytest.mark.parametrize("text,min_length,max_length", [
        ("Hi", 10, False),  # Tweet très court
        ("A" * 50, 10, 280),  # Tweet normal
        ("A" * 300, 280, 300),  # Tweet long
    ])
    def test_tweet_lengths(self, cleaner, text, min_length, max_length):
        """Teste avec différentes longueurs de tweets"""
        result = cleaner.clean_for_analysis(text)
        assert isinstance(result, str)


class TestHandleSpecialCases:
    """Tests pour handle_special_cases"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_empty_text_detection(self, cleaner):
        """Teste la détection de texte vide"""
        result = cleaner.handle_special_cases("")
        assert result['is_empty'] is True
        assert result['is_too_short'] is True
    
    def test_short_text_detection(self, cleaner):
        """Teste la détection de texte trop court"""
        result = cleaner.handle_special_cases("Hi")
        assert result['is_too_short'] is True
        assert result['is_empty'] is False
    
    def test_long_text_detection(self, cleaner):
        """Teste la détection de texte trop long"""
        long_text = "A" * 300
        result = cleaner.handle_special_cases(long_text)
        assert result['is_too_long'] is True
    
    def test_normal_length(self, cleaner):
        """Teste un texte de longueur normale"""
        text = "This is a normal length tweet about something"
        result = cleaner.handle_special_cases(text)
        assert result['is_too_short'] is False
        assert result['is_too_long'] is False
    
    def test_irony_detection(self, cleaner):
        """Teste la détection de marqueurs d'ironie"""
        ironic_texts = [
            "Super service lol",
            "Génial mdr",
            "Top /s",
            "Excellent 😂"
        ]
        for text in ironic_texts:
            result = cleaner.handle_special_cases(text)
            assert result['has_irony_markers'] is True
    
    def test_unicode_issues(self, cleaner):
        """Teste la détection de problèmes Unicode"""
        # Texte normal
        result = cleaner.handle_special_cases("Normal text")
        assert result['has_unicode_issues'] is False


class TestNormalizeText:
    """Tests pour normalize_text"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_lowercase_conversion(self, cleaner):
        """Teste la conversion en minuscules"""
        text = "Hello WORLD"
        result = cleaner.normalize_text(text, lowercase=True)
        assert result == "hello world"
    
    def test_keep_case(self, cleaner):
        """Teste la préservation de la casse"""
        text = "Hello WORLD"
        result = cleaner.normalize_text(text, lowercase=False)
        assert "Hello" in result
        assert "WORLD" in result
    
    def test_unicode_normalization(self, cleaner):
        """Teste la normalisation Unicode"""
        text = "café"
        result = cleaner.normalize_text(text)
        assert isinstance(result, str)


class TestExtractKeywords:
    """Tests pour extract_keywords"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_basic_extraction(self, cleaner):
        """Teste l'extraction basique de mots-clés"""
        text = "Le service internet est excellent et rapide"
        keywords = cleaner.extract_keywords(text)
        
        # Doit exclure les stopwords
        assert "le" not in keywords
        assert "est" not in keywords
        
        # Doit inclure les mots significatifs
        assert any(k in keywords for k in ["service", "internet", "excellent", "rapide"])
    
    def test_min_length_filter(self, cleaner):
        """Teste le filtre de longueur minimale"""
        text = "Le service ok est top"
        keywords = cleaner.extract_keywords(text, min_length=4)
        
        # "ok" (2 lettres) doit être exclu
        assert "ok" not in keywords
    
    def test_max_keywords_limit(self, cleaner):
        """Teste la limite du nombre de mots-clés"""
        text = " ".join([f"word{i}" for i in range(20)])
        keywords = cleaner.extract_keywords(text, max_keywords=5)
        
        assert len(keywords) <= 5
    
    def test_empty_text_keywords(self, cleaner):
        """Teste avec texte vide"""
        keywords = cleaner.extract_keywords("")
        assert keywords == []
    
    def test_only_stopwords(self, cleaner):
        """Teste avec seulement des stopwords"""
        text = "le de et à un il"
        keywords = cleaner.extract_keywords(text)
        assert len(keywords) == 0


class TestIsSpamLike:
    """Tests pour is_spam_like"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_empty_is_spam(self, cleaner):
        """Teste que texte vide est considéré comme spam"""
        assert cleaner.is_spam_like("") is True
        assert cleaner.is_spam_like("abc") is True  # Trop court
    
    def test_excessive_repetition(self, cleaner):
        """Teste la détection de répétition excessive"""
        text = "buy buy buy buy buy buy"
        assert cleaner.is_spam_like(text) is True
    
    def test_excessive_mentions(self, cleaner):
        """Teste la détection de mentions excessives"""
        text = " ".join([f"@user{i}" for i in range(10)])
        assert cleaner.is_spam_like(text) is True
    
    def test_excessive_hashtags(self, cleaner):
        """Teste la détection de hashtags excessifs"""
        text = " ".join([f"#tag{i}" for i in range(10)])
        assert cleaner.is_spam_like(text) is True
    
    def test_excessive_urls(self, cleaner):
        """Teste la détection d'URLs excessives"""
        text = " ".join([f"https://site{i}.com" for i in range(5)])
        assert cleaner.is_spam_like(text) is True
    
    def test_excessive_caps(self, cleaner):
        """Teste la détection de majuscules excessives"""
        text = "BUY NOW THIS AMAZING PRODUCT"
        assert cleaner.is_spam_like(text) is True
    
    def test_normal_text_not_spam(self, cleaner):
        """Teste qu'un texte normal n'est pas spam"""
        text = "Bonjour, j'ai un problème avec mon abonnement"
        assert cleaner.is_spam_like(text) is False


class TestEdgeCases:
    """Tests pour les cas limites"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    @pytest.mark.parametrize("text", [
        "😊😭😡😍🎉",  # Seulement emojis
        "@user1 @user2 @user3",  # Seulement mentions
        "#tag1 #tag2 #tag3",  # Seulement hashtags
        "https://url1.com https://url2.com",  # Seulement URLs
    ])
    def test_special_only_texts(self, cleaner, text):
        """Teste avec seulement des éléments spéciaux"""
        result = cleaner.clean_for_analysis(
            text,
            preserve_mentions=False,
            preserve_hashtags=False,
            preserve_emojis=False
        )
        # Devrait retourner une chaîne vide ou très courte
        assert len(result) < len(text)
    
    def test_mixed_languages(self, cleaner):
        """Teste avec texte multilangue"""
        text = "Hello world 你好 مرحبا"
        result = cleaner.clean_basic(text)
        assert isinstance(result, str)
    
    def test_very_long_word(self, cleaner):
        """Teste avec mot très long"""
        text = "A" * 1000
        result = cleaner.clean_for_analysis(text)
        assert isinstance(result, str)
    
    def test_special_unicode_characters(self, cleaner):
        """Teste avec caractères Unicode spéciaux"""
        text = "Test™ with® special© characters"
        result = cleaner.clean_basic(text)
        assert isinstance(result, str)


class TestRobustness:
    """Tests de robustesse"""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_none_input(self, cleaner):
        """Teste avec None en entrée"""
        assert cleaner.clean_basic(None) == ""
        assert cleaner.clean_for_analysis(None) == ""
    
    def test_non_string_input(self, cleaner):
        """Teste avec types non-string"""
        assert cleaner.clean_basic(123) == ""
        assert cleaner.clean_basic([]) == ""
    
    def test_multiple_operations(self, cleaner):
        """Teste des opérations successives"""
        text = "@user Check https://url.com #topic 😊"
        
        step1 = cleaner.clean_basic(text)
        step2 = cleaner.remove_urls(step1)
        step3 = cleaner.remove_emojis(step2)
        
        assert isinstance(step3, str)
        assert "https://" not in step3
        assert "😊" not in step3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

