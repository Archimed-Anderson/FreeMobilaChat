#!/usr/bin/env python3
"""
Script pour supprimer tous les emojis du code
"""

import re
from pathlib import Path

def remove_emojis_from_file(file_path):
    """Supprime les emojis d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern pour détecter les emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        
        # Supprimer les emojis
        new_content = emoji_pattern.sub('', content)
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Emojis supprimés de: {file_path}")
            return True
        else:
            print(f"Aucun emoji trouvé dans: {file_path}")
            return False
            
    except Exception as e:
        print(f"Erreur avec {file_path}: {e}")
        return False

def main():
    """Fonction principale"""
    
    print("Suppression des emojis du code...")
    print("=" * 50)
    
    # Répertoires à traiter
    directories = [
        Path("pages"),
        Path("components"),
        Path("services"),
        Path("utils"),
        Path("config")
    ]
    
    # Extensions de fichiers à traiter
    extensions = ['.py', '.md']
    
    files_processed = 0
    files_modified = 0
    
    for directory in directories:
        if not directory.exists():
            continue
            
        for ext in extensions:
            for file_path in directory.rglob(f"*{ext}"):
                if file_path.is_file():
                    files_processed += 1
                    if remove_emojis_from_file(file_path):
                        files_modified += 1
    
    print(f"\n{'='*50}")
    print(f"Fichiers traités: {files_processed}")
    print(f"Fichiers modifiés: {files_modified}")
    print("Terminé!")

if __name__ == "__main__":
    main()

