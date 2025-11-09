"""
Configuration globale pytest
Fixtures partagées pour tous les tests
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture pour le répertoire de données de test"""
    return Path("storage/datasets")


@pytest.fixture
def sample_tweet_text():
    """Fixture avec exemples de tweets"""
    return [
        "Service excellent merci beaucoup! 😊",
        "Problème réseau encore une fois, c'est inadmissible!",
        "Bonjour, quelle est la procédure pour changer mon forfait?",
        "@Free le débit est nul depuis 3 jours 😡",
        "Merci pour votre aide rapide et efficace",
    ]


@pytest.fixture
def sample_csv_data():
    """Fixture avec données CSV de test"""
    return """tweet_id,author,text,date
1,user1,Service excellent merci!,2024-01-01 10:00:00
2,user2,Problème réseau catastrophique,2024-01-02 11:30:00
3,user3,Information sur abonnement,2024-01-03 14:15:00
4,user4,@Free le débit est nul,2024-01-04 16:45:00
5,user5,Merci pour votre aide,2024-01-05 09:20:00
"""


@pytest.fixture
def temp_csv_file(sample_csv_data):
    """Fixture qui crée un fichier CSV temporaire"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(sample_csv_data)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except:
        pass


@pytest.fixture
def temp_directory():
    """Fixture qui crée un répertoire temporaire"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup
    try:
        import shutil
        shutil.rmtree(temp_dir)
    except:
        pass


# Configuration pour les tests asyncio
@pytest.fixture(scope="session")
def event_loop_policy():
    """Configure la politique de boucle d'événements pour les tests async"""
    import asyncio
    return asyncio.get_event_loop_policy()


# Markers de configuration
def pytest_configure(config):
    """Configuration pytest personnalisée"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )


def pytest_collection_modifyitems(config, items):
    """Modifier les items de test collectés"""
    # Ajouter automatiquement les markers basés sur le chemin
    for item in items:
        if "units" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

