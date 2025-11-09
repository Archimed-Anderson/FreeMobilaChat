"""
Tests unitaires pour le module read_file
Validation de la robustesse de la lecture de fichiers CSV
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from src.utils.file_handlers.read_file import (
    readCSV, 
    validateCSVColumns, 
    readTweetsCSV
)


class TestReadFile:
    """Tests pour la fonction readCSV"""
    
    @pytest.mark.parametrize("path,expected", [
        ("storage/datasets/dataset.csv", True),
        ("invalid_path.csv", False)
    ])
    def test_file_loading(self, path, expected):
        """Teste le chargement avec différents chemins"""
        if expected:
            df = readCSV(path)
            assert not df.empty
            assert isinstance(df, pd.DataFrame)
        else:
            with pytest.raises(FileNotFoundError):
                readCSV(path)
    
    def test_relative_path(self):
        """Teste le chargement avec chemin relatif"""
        df = readCSV("storage/datasets/dataset.csv")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_absolute_path(self):
        """Teste le chargement avec chemin absolu"""
        abs_path = Path("storage/datasets/dataset.csv").absolute()
        df = readCSV(abs_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_path_object(self):
        """Teste le chargement avec objet Path"""
        path = Path("storage/datasets/dataset.csv")
        df = readCSV(path)
        assert isinstance(df, pd.DataFrame)
    
    def test_empty_file(self):
        """Teste la gestion d'un fichier CSV vide"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            f.write("col1,col2\n")  # Headers only
        
        try:
            with pytest.raises(ValueError, match="vide"):
                readCSV(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_malformed_csv(self):
        """Teste la gestion d'un CSV mal formaté"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            f.write("col1,col2\n")
            f.write("val1\n")  # Ligne incomplète
            f.write("val2,val3,val4\n")  # Ligne avec trop de colonnes
        
        try:
            # Pandas peut gérer certaines malformations
            df = readCSV(temp_path)
            # Vérifier que ça charge quand même quelque chose
            assert isinstance(df, pd.DataFrame)
        finally:
            os.unlink(temp_path)
    
    def test_file_not_found(self):
        """Teste l'erreur pour fichier inexistant"""
        with pytest.raises(FileNotFoundError):
            readCSV("nonexistent_file.csv")
    
    def test_unicode_handling(self):
        """Teste la gestion des caractères Unicode"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            temp_path = f.name
            f.write("text\n")
            f.write("Été ☀️\n")
            f.write("Noël 🎄\n")
            f.write("Café ☕\n")
        
        try:
            df = readCSV(temp_path)
            assert len(df) == 3
            assert 'Été' in df['text'].values[0]
        finally:
            os.unlink(temp_path)


class TestValidateCSVColumns:
    """Tests pour la fonction validateCSVColumns"""
    
    def test_valid_columns(self):
        """Teste la validation avec colonnes correctes"""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c'],
            'col3': [True, False, True]
        })
        
        assert validateCSVColumns(df, ['col1', 'col2']) is True
        assert validateCSVColumns(df, ['col1', 'col2', 'col3']) is True
    
    def test_missing_columns(self):
        """Teste la détection de colonnes manquantes"""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        with pytest.raises(ValueError, match="Colonnes manquantes"):
            validateCSVColumns(df, ['col1', 'col2', 'col3'])
    
    def test_empty_required_columns(self):
        """Teste avec liste de colonnes requises vide"""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        assert validateCSVColumns(df, []) is True
    
    def test_all_columns_missing(self):
        """Teste quand toutes les colonnes requises manquent"""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        
        with pytest.raises(ValueError, match="col2.*col3"):
            validateCSVColumns(df, ['col2', 'col3'])


class TestReadTweetsCSV:
    """Tests pour la fonction readTweetsCSV"""
    
    def test_valid_tweets_csv(self):
        """Teste le chargement d'un CSV de tweets valide"""
        df = readTweetsCSV("storage/datasets/dataset.csv")
        
        # Vérifier les colonnes requises
        assert 'tweet_id' in df.columns
        assert 'author' in df.columns
        assert 'text' in df.columns
        assert 'date' in df.columns
        
        # Vérifier qu'il y a des données
        assert len(df) > 0
    
    def test_missing_tweet_columns(self):
        """Teste l'erreur si colonnes de tweets manquantes"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            f.write("id,content\n")
            f.write("1,test\n")
        
        try:
            with pytest.raises(ValueError, match="Colonnes manquantes"):
                readTweetsCSV(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_tweets_data_integrity(self):
        """Teste l'intégrité des données de tweets"""
        df = readTweetsCSV("storage/datasets/dataset.csv")
        
        # Vérifier qu'il n'y a pas de valeurs nulles dans les colonnes essentielles
        assert df['tweet_id'].notna().all()
        assert df['text'].notna().all()
        
        # Vérifier les types
        assert df['tweet_id'].dtype == object or df['tweet_id'].dtype == 'int64'
        assert df['text'].dtype == object


class TestEdgeCases:
    """Tests pour les cas limites"""
    
    def test_very_large_file(self):
        """Teste le chargement d'un fichier avec beaucoup de lignes"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            f.write("tweet_id,author,text,date\n")
            for i in range(10000):
                f.write(f"{i},user{i},text{i},2024-01-01\n")
        
        try:
            df = readCSV(temp_path)
            assert len(df) == 10000
        finally:
            os.unlink(temp_path)
    
    def test_special_characters_in_path(self):
        """Teste les chemins avec caractères spéciaux"""
        # Windows n'aime pas certains caractères dans les noms de fichiers
        # On teste juste les espaces
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=' test.csv', 
            delete=False,
            dir='.'
        ) as f:
            temp_path = f.name
            f.write("col1,col2\n")
            f.write("val1,val2\n")
        
        try:
            df = readCSV(temp_path)
            assert len(df) == 1
        finally:
            os.unlink(temp_path)
    
    def test_csv_with_quotes(self):
        """Teste un CSV avec guillemets"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            f.write('text\n')
            f.write('"Hello, World!"\n')
            f.write('"He said ""OK"""\n')
        
        try:
            df = readCSV(temp_path)
            assert len(df) == 2
            assert df['text'].iloc[0] == 'Hello, World!'
        finally:
            os.unlink(temp_path)
    
    def test_csv_with_newlines_in_fields(self):
        """Teste un CSV avec retours à la ligne dans les champs"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            f.write('text\n')
            f.write('"Line 1\nLine 2"\n')
            f.write('"Single line"\n')
        
        try:
            df = readCSV(temp_path)
            assert len(df) == 2
        finally:
            os.unlink(temp_path)


class TestPerformance:
    """Tests de performance"""
    
    def test_loading_time(self):
        """Teste que le chargement respecte un temps limite"""
        import time
        
        start = time.time()
        df = readCSV("storage/datasets/dataset.csv")
        duration = time.time() - start
        
        # Le chargement doit prendre moins de 5 secondes
        assert duration < 5.0, f"Chargement trop lent: {duration:.2f}s"
    
    def test_memory_efficiency(self):
        """Teste que le DataFrame n'est pas trop volumineux"""
        df = readCSV("storage/datasets/dataset.csv")
        
        # Vérifier la taille mémoire
        memory_usage = df.memory_usage(deep=True).sum()
        memory_mb = memory_usage / (1024 * 1024)
        
        # Devrait être raisonnable (moins de 100 MB pour un fichier de tweets)
        assert memory_mb < 100, f"Utilisation mémoire excessive: {memory_mb:.2f} MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

