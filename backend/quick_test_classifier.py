"""
Script de Test Rapide du Classificateur
========================================

Ce script permet de tester rapidement le module de classification
sans avoir besoin d'une API key (mode fallback).

Usage:
    python quick_test_classifier.py
"""

import sys
from pathlib import Path

# Ajouter le chemin backend au sys.path
backend_path = Path(__file__).parent
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

from app.services.tweet_classifier import TweetClassifier, classify_tweet

# Tweets de test
TEST_TWEETS = [
    {
        "tweet": "@Free Ma fibre est coupée depuis ce matin, c'est insupportable !",
        "expected": {
            "is_reclamation": "OUI",
            "theme": "FIBRE",
            "sentiment": "NEGATIF",
            "urgence": "ELEVEE"
        }
    },
    {
        "tweet": "@Free Merci pour le déploiement rapide de la fibre dans ma ville !",
        "expected": {
            "is_reclamation": "NON",
            "sentiment": "POSITIF",
            "type_incident": "INFO"
        }
    },
    {
        "tweet": "@Free Mon mobile a un débit 4G très lent depuis hier",
        "expected": {
            "is_reclamation": "OUI",
            "theme": "MOBILE",
            "type_incident": "LENTEUR"
        }
    },
    {
        "tweet": "@Free Ma facture est anormalement élevée ce mois-ci, pouvez-vous vérifier ?",
        "expected": {
            "is_reclamation": "OUI",
            "theme": "FACTURE",
            "type_incident": "FACTURATION"
        }
    },
    {
        "tweet": "@Free Aucune réponse du SAV depuis 2 semaines, c'est inadmissible !",
        "expected": {
            "is_reclamation": "OUI",
            "theme": "SAV",
            "type_incident": "PROCESSUS_SAV"
        }
    }
]


def print_separator(char="=", length=80):
    """Affiche un séparateur"""
    print(char * length)


def print_result(tweet, result, expected):
    """Affiche un résultat de classification"""
    print(f"\n📝 Tweet: {tweet}")
    print_separator("-", 80)
    
    print(f"✓ Réclamation: {result.is_reclamation}")
    print(f"✓ Thème: {result.theme}")
    print(f"✓ Sentiment: {result.sentiment}")
    print(f"✓ Urgence: {result.urgence}")
    print(f"✓ Type d'incident: {result.type_incident}")
    print(f"✓ Confiance: {result.confidence:.2f}")
    print(f"✓ Justification: {result.justification}")
    
    # Vérifier les attentes
    checks_passed = 0
    checks_total = 0
    
    print("\n🔍 Vérifications:")
    for key, value in expected.items():
        checks_total += 1
        actual = getattr(result, key)
        if actual == value:
            print(f"  ✅ {key}: {actual} (attendu: {value})")
            checks_passed += 1
        else:
            print(f"  ❌ {key}: {actual} (attendu: {value})")
    
    accuracy = (checks_passed / checks_total) * 100 if checks_total > 0 else 0
    print(f"\n📊 Score: {checks_passed}/{checks_total} ({accuracy:.1f}%)")


def main():
    """Fonction principale"""
    print_separator()
    print("  TEST RAPIDE DU CLASSIFICATEUR DE TWEETS FREE")
    print_separator()
    
    print("\n🚀 Initialisation du classificateur en mode FALLBACK (sans LLM)")
    print("   (Aucune API key requise, classification par règles)\n")
    
    # Initialiser le classificateur en mode fallback
    classifier = TweetClassifier(
        model_name="fallback",
        api_key=None
    )
    
    print(f"✅ Classificateur initialisé: {classifier.provider}")
    print_separator()
    
    # Tester chaque tweet
    total_accuracy = 0
    
    for i, test in enumerate(TEST_TWEETS, 1):
        print(f"\n\n🔢 TEST {i}/{len(TEST_TWEETS)}")
        
        tweet = test["tweet"]
        expected = test["expected"]
        
        # Classifier
        result = classifier.classify(tweet)
        
        # Afficher le résultat
        print_result(tweet, result, expected)
        
        # Calculer l'accuracy pour ce test
        checks_passed = sum(
            1 for key, value in expected.items()
            if getattr(result, key) == value
        )
        test_accuracy = (checks_passed / len(expected)) * 100
        total_accuracy += test_accuracy
    
    # Résumé final
    print("\n\n")
    print_separator("=", 80)
    print("  RÉSUMÉ DES TESTS")
    print_separator("=", 80)
    
    avg_accuracy = total_accuracy / len(TEST_TWEETS)
    
    print(f"\n📊 Accuracy Moyenne: {avg_accuracy:.1f}%")
    print(f"📝 Tests Exécutés: {len(TEST_TWEETS)}")
    
    if avg_accuracy >= 80:
        print("\n✅ SUCCÈS ! Le classificateur fonctionne correctement.")
    elif avg_accuracy >= 60:
        print("\n⚠️  ACCEPTABLE. Le classificateur fonctionne mais pourrait être amélioré.")
    else:
        print("\n❌ ÉCHEC. Le classificateur nécessite des améliorations.")
    
    print("\n💡 Note: Ces tests utilisent le mode FALLBACK (règles simples).")
    print("   Pour des résultats optimaux, utilisez un LLM (GPT-4, Claude, etc.)")
    print_separator("=", 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

