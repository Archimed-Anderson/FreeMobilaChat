"""
Module de lecture de fichiers CSV
Gestion robuste des fichiers avec validation
"""

import pandas as pd
from pathlib import Path
from typing import Union, Optional


def readCSV(path: Union[str, Path]) -> pd.DataFrame:
    """
    Charge un fichier CSV avec gestion d'erreur
    
    Args:
        path: Chemin vers le fichier CSV (relatif ou absolu)
        
    Returns:
        DataFrame pandas contenant les données
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        ValueError: Si le fichier est vide ou mal formaté
        
    Examples:
        >>> df = readCSV("storage/datasets/dataset.csv")
        >>> df = readCSV(Path("data/tweets.csv"))
    """
    try:
        # Convertir en Path pour gérer les chemins relatifs/absolus
        file_path = Path(path)
        
        # Vérifier l'existence du fichier
        if not file_path.exists():
            raise FileNotFoundError(f"Le fichier {path} n'existe pas")
        
        # Lire le CSV
        df = pd.read_csv(file_path)
        
        # Vérifier que le DataFrame n'est pas vide
        if df.empty:
            raise ValueError(f"Le fichier {path} est vide")
            
        return df
        
    except FileNotFoundError:
        raise
    except pd.errors.EmptyDataError:
        raise ValueError(f"Le fichier {path} est vide ou mal formaté")
    except pd.errors.ParserError as e:
        raise ValueError(f"Erreur de parsing CSV dans {path}: {str(e)}")
    except Exception as e:
        raise FileNotFoundError(f"Erreur lecture {path} : {str(e)}")


def validateCSVColumns(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Valide que le DataFrame contient les colonnes requises
    
    Args:
        df: DataFrame à valider
        required_columns: Liste des colonnes requises
        
    Returns:
        True si toutes les colonnes sont présentes
        
    Raises:
        ValueError: Si des colonnes manquent
    """
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        raise ValueError(f"Colonnes manquantes: {', '.join(missing_columns)}")
    
    return True


def readTweetsCSV(path: Union[str, Path]) -> pd.DataFrame:
    """
    Charge un fichier CSV de tweets avec validation des colonnes
    
    Args:
        path: Chemin vers le fichier CSV
        
    Returns:
        DataFrame validé contenant les tweets
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        ValueError: Si les colonnes requises manquent
    """
    df = readCSV(path)
    
    # Colonnes attendues pour un dataset de tweets
    required_columns = ['tweet_id', 'author', 'text', 'date']
    
    validateCSVColumns(df, required_columns)
    
    return df

