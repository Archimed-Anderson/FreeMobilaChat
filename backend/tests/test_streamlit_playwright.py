#!/usr/bin/env python3
"""
Script de test Playwright pour l'interface Streamlit du Chatbot SAV FreeMobilaChat
Phase 2.1 - Étape 5: Tests Playwright de l'Interface
"""

import asyncio
import time
from typing import List, Dict, Any
import json

def test_streamlit_interface():
    """
    Test de l'interface Streamlit avec les outils Playwright disponibles.
    
    Tests à effectuer:
    1. Navigation vers http://localhost:8501
    2. Accès à la page '💬 Chatbot SAV'
    3. Test de sélection du provider LLM
    4. Test du bouton d'initialisation
    5. Test d'envoi de message
    6. Vérification de la réponse
    7. Test des sources affichées
    8. Vérification des statistiques
    """
    
    print("🎭 TESTS PLAYWRIGHT - INTERFACE STREAMLIT CHATBOT")
    print("=" * 60)
    
    # Liste des tests à effectuer
    tests = [
        {
            "name": "Navigation vers Streamlit",
            "description": "Accéder à http://localhost:8501",
            "action": "navigate",
            "url": "http://localhost:8501"
        },
        {
            "name": "Accès page Chatbot SAV", 
            "description": "Cliquer sur '💬 Chatbot SAV' dans la sidebar",
            "action": "click_sidebar_page",
            "target": "💬 Chatbot SAV"
        },
        {
            "name": "Sélection provider LLM",
            "description": "Changer le provider dans la sidebar",
            "action": "select_option",
            "target": "Fournisseur IA",
            "value": "mistral"
        },
        {
            "name": "Initialisation chatbot",
            "description": "Cliquer sur '🚀 Initialiser le chatbot'",
            "action": "click_button",
            "target": "🚀 Initialiser le chatbot"
        },
        {
            "name": "Envoi message test",
            "description": "Envoyer un message de test",
            "action": "send_message",
            "message": "Bonjour, j'ai un problème avec mon forfait Free Mobile"
        },
        {
            "name": "Vérification réponse",
            "description": "Vérifier que le chatbot répond",
            "action": "check_response",
            "expected": "assistant"
        },
        {
            "name": "Test sources",
            "description": "Vérifier l'affichage des sources",
            "action": "check_sources",
            "expected": "Sources"
        },
        {
            "name": "Statistiques conversation",
            "description": "Vérifier les stats dans la sidebar",
            "action": "check_stats",
            "expected": "Messages"
        }
    ]
    
    print(f"📋 {len(tests)} tests planifiés:")
    for i, test in enumerate(tests, 1):
        print(f"  {i}. {test['name']} - {test['description']}")
    
    print("\n" + "=" * 60)
    print("⚠️  INSTRUCTIONS POUR EXÉCUTION MANUELLE:")
    print("=" * 60)
    print("1. Utiliser les outils Playwright disponibles:")
    print("   - browser_navigate_Playwright")
    print("   - browser_snapshot_Playwright") 
    print("   - browser_click_Playwright")
    print("   - browser_type_Playwright")
    print("   - browser_select_option_Playwright")
    print("   - browser_take_screenshot_Playwright")
    
    print("\n2. Séquence de tests recommandée:")
    for i, test in enumerate(tests, 1):
        print(f"   {i}. {test['action']}: {test['description']}")
        if 'url' in test:
            print(f"      URL: {test['url']}")
        if 'target' in test:
            print(f"      Cible: {test['target']}")
        if 'value' in test:
            print(f"      Valeur: {test['value']}")
        if 'message' in test:
            print(f"      Message: {test['message']}")
        print()
    
    print("3. Captures d'écran à prendre:")
    print("   - Page d'accueil Streamlit")
    print("   - Page Chatbot SAV")
    print("   - Interface de chat avec message")
    print("   - Réponse du chatbot")
    print("   - Sidebar avec statistiques")
    
    print("\n4. Bugs/UX à documenter:")
    print("   - Temps de chargement")
    print("   - Erreurs d'affichage")
    print("   - Problèmes de navigation")
    print("   - Interface non responsive")
    print("   - Messages d'erreur")
    
    return tests

def generate_test_report(results: List[Dict[str, Any]]) -> str:
    """Génère un rapport de test formaté."""
    
    report = []
    report.append("# 📊 RAPPORT DE TESTS PLAYWRIGHT - CHATBOT SAV")
    report.append("=" * 60)
    report.append(f"📅 Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"🌐 URL testée: http://localhost:8501")
    report.append(f"📱 Page: 💬 Chatbot SAV")
    report.append("")
    
    # Résumé
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get('status') == 'PASS')
    failed_tests = total_tests - passed_tests
    
    report.append("## 📈 RÉSUMÉ")
    report.append(f"- ✅ Tests réussis: {passed_tests}/{total_tests}")
    report.append(f"- ❌ Tests échoués: {failed_tests}/{total_tests}")
    report.append(f"- 📊 Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
    report.append("")
    
    # Détails des tests
    report.append("## 🔍 DÉTAILS DES TESTS")
    for i, result in enumerate(results, 1):
        status_icon = "✅" if result.get('status') == 'PASS' else "❌"
        report.append(f"### {i}. {status_icon} {result.get('name', 'Test')}")
        report.append(f"**Description:** {result.get('description', 'N/A')}")
        report.append(f"**Statut:** {result.get('status', 'UNKNOWN')}")
        
        if result.get('duration'):
            report.append(f"**Durée:** {result['duration']:.2f}s")
        
        if result.get('error'):
            report.append(f"**Erreur:** {result['error']}")
        
        if result.get('screenshot'):
            report.append(f"**Capture:** {result['screenshot']}")
        
        report.append("")
    
    # Recommandations
    report.append("## 🎯 RECOMMANDATIONS")
    if failed_tests > 0:
        report.append("### ⚠️ Problèmes identifiés:")
        for result in results:
            if result.get('status') == 'FAIL':
                report.append(f"- {result.get('name')}: {result.get('error', 'Erreur inconnue')}")
        report.append("")
    
    report.append("### 🔧 Améliorations suggérées:")
    report.append("- Optimiser les temps de chargement")
    report.append("- Améliorer la responsivité mobile")
    report.append("- Ajouter des indicateurs de chargement")
    report.append("- Améliorer les messages d'erreur")
    report.append("")
    
    return "\n".join(report)

if __name__ == "__main__":
    # Exécution du script de test
    tests = test_streamlit_interface()
    
    print("\n🚀 Pour exécuter les tests, utilisez les outils Playwright disponibles")
    print("📝 Documentez les résultats pour générer le rapport final")
