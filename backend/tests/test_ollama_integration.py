#!/usr/bin/env python3
"""
Test complet de l'intégration Ollama avec l'Agent Agno
"""
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any


class OllamaIntegrationTester:
    """Testeur d'intégration Ollama"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.chatbot_endpoint = f"{api_url}/api/chatbot/message"
        self.test_results = []
        
    def print_header(self, title: str):
        """Afficher un en-tête formaté"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def print_test_result(self, test_name: str, success: bool, details: str = ""):
        """Afficher le résultat d'un test"""
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"\n{status}: {test_name}")
        if details:
            print(f"  Détails: {details}")
    
    def send_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Envoyer un message au chatbot"""
        if session_id is None:
            session_id = f"test_ollama_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        payload = {
            "message": message,
            "session_id": session_id,
            "llm_provider": "ollama"
        }
        
        try:
            start_time = time.time()
            response = requests.post(self.chatbot_endpoint, json=payload, timeout=120)
            elapsed_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "elapsed_time": elapsed_time
                }
            
            result = response.json()
            result["elapsed_time"] = elapsed_time
            result["success"] = True
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "elapsed_time": 0
            }
    
    def test_simple_question(self) -> bool:
        """Test 1: Question simple"""
        self.print_header("TEST 1: QUESTION SIMPLE")
        
        message = "Bonjour, comment vas-tu ?"
        print(f"Question: {message}")
        
        result = self.send_message(message)
        
        if not result["success"]:
            self.print_test_result("Question simple", False, result.get("error", "Erreur inconnue"))
            return False
        
        response_text = result.get("response", "")
        conversation_id = result.get("conversation_id", "N/A")
        processing_time = result.get("processing_time", 0)
        llm_provider = result.get("llm_provider", "N/A")
        
        # Vérifier que ce n'est pas une réponse simulée
        is_simulated = any(phrase in response_text for phrase in [
            "Je suis en cours de développement",
            "difficultés techniques",
            "réessayer dans quelques instants"
        ])
        
        print(f"\nRéponse ({len(response_text)} caractères):")
        print(f"  {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
        print(f"\nMétadonnées:")
        print(f"  - Conversation ID: {conversation_id}")
        print(f"  - LLM Provider: {llm_provider}")
        print(f"  - Temps de traitement: {processing_time:.2f}s")
        print(f"  - Temps total: {result['elapsed_time']:.2f}s")
        
        success = not is_simulated and llm_provider == "ollama"
        self.print_test_result(
            "Question simple",
            success,
            "Réponse générée par Ollama" if success else "Réponse simulée ou provider incorrect"
        )
        
        self.test_results.append(("Question simple", success))
        return success
    
    def test_technical_question(self) -> bool:
        """Test 2: Question technique Free Mobile"""
        self.print_header("TEST 2: QUESTION TECHNIQUE FREE MOBILE")
        
        message = "Comment activer la 4G sur mon téléphone Free Mobile ?"
        print(f"Question: {message}")
        
        result = self.send_message(message)
        
        if not result["success"]:
            self.print_test_result("Question technique", False, result.get("error", "Erreur inconnue"))
            return False
        
        response_text = result.get("response", "")
        llm_provider = result.get("llm_provider", "N/A")
        processing_time = result.get("processing_time", 0)
        
        # Vérifier que ce n'est pas une réponse simulée
        is_simulated = any(phrase in response_text for phrase in [
            "Je suis en cours de développement",
            "difficultés techniques",
            "réessayer dans quelques instants"
        ])
        
        print(f"\nRéponse ({len(response_text)} caractères):")
        print(f"  {response_text[:300]}{'...' if len(response_text) > 300 else ''}")
        print(f"\nMétadonnées:")
        print(f"  - LLM Provider: {llm_provider}")
        print(f"  - Temps de traitement: {processing_time:.2f}s")
        print(f"  - Temps total: {result['elapsed_time']:.2f}s")
        
        success = not is_simulated and llm_provider == "ollama"
        self.print_test_result(
            "Question technique",
            success,
            "Réponse générée par Ollama" if success else "Réponse simulée ou provider incorrect"
        )
        
        self.test_results.append(("Question technique", success))
        return success
    
    def test_complex_question(self) -> bool:
        """Test 3: Question complexe avec contexte"""
        self.print_header("TEST 3: QUESTION COMPLEXE AVEC CONTEXTE")
        
        session_id = f"test_complex_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Première question pour établir le contexte
        message1 = "Je viens de souscrire à un forfait Free Mobile 5G."
        print(f"Message 1: {message1}")
        
        result1 = self.send_message(message1, session_id)
        
        if not result1["success"]:
            self.print_test_result("Question complexe (message 1)", False, result1.get("error", "Erreur inconnue"))
            return False
        
        print(f"Réponse 1: {result1.get('response', '')[:150]}...")
        
        # Deuxième question qui nécessite le contexte
        time.sleep(1)  # Petit délai entre les messages
        message2 = "Quels sont les avantages de ce forfait ?"
        print(f"\nMessage 2: {message2}")
        
        result2 = self.send_message(message2, session_id)
        
        if not result2["success"]:
            self.print_test_result("Question complexe (message 2)", False, result2.get("error", "Erreur inconnue"))
            return False
        
        response_text = result2.get("response", "")
        llm_provider = result2.get("llm_provider", "N/A")
        processing_time = result2.get("processing_time", 0)
        
        # Vérifier que ce n'est pas une réponse simulée
        is_simulated = any(phrase in response_text for phrase in [
            "Je suis en cours de développement",
            "difficultés techniques",
            "réessayer dans quelques instants"
        ])
        
        print(f"\nRéponse 2 ({len(response_text)} caractères):")
        print(f"  {response_text[:300]}{'...' if len(response_text) > 300 else ''}")
        print(f"\nMétadonnées:")
        print(f"  - LLM Provider: {llm_provider}")
        print(f"  - Temps de traitement: {processing_time:.2f}s")
        print(f"  - Temps total: {result2['elapsed_time']:.2f}s")
        
        success = not is_simulated and llm_provider == "ollama"
        self.print_test_result(
            "Question complexe",
            success,
            "Réponse générée par Ollama avec contexte" if success else "Réponse simulée ou provider incorrect"
        )
        
        self.test_results.append(("Question complexe", success))
        return success
    
    def test_response_quality(self) -> bool:
        """Test 4: Qualité des réponses"""
        self.print_header("TEST 4: QUALITÉ DES RÉPONSES")
        
        message = "Explique-moi en 3 points comment configurer mon APN Free Mobile."
        print(f"Question: {message}")
        
        result = self.send_message(message)
        
        if not result["success"]:
            self.print_test_result("Qualité des réponses", False, result.get("error", "Erreur inconnue"))
            return False
        
        response_text = result.get("response", "")
        llm_provider = result.get("llm_provider", "N/A")
        
        # Critères de qualité
        is_not_simulated = not any(phrase in response_text for phrase in [
            "Je suis en cours de développement",
            "difficultés techniques",
            "réessayer dans quelques instants"
        ])
        
        has_structure = any(marker in response_text for marker in ["1.", "2.", "3.", "-", "*", "•"])
        has_sufficient_length = len(response_text) > 100
        is_ollama = llm_provider == "ollama"
        
        print(f"\nRéponse ({len(response_text)} caractères):")
        print(response_text)
        print(f"\nCritères de qualité:")
        print(f"  - Pas de réponse simulée: {'✅' if is_not_simulated else '❌'}")
        print(f"  - Structure (points/liste): {'✅' if has_structure else '❌'}")
        print(f"  - Longueur suffisante (>100 car): {'✅' if has_sufficient_length else '❌'}")
        print(f"  - Provider Ollama: {'✅' if is_ollama else '❌'}")
        
        success = is_not_simulated and has_structure and has_sufficient_length and is_ollama
        self.print_test_result(
            "Qualité des réponses",
            success,
            "Réponse de qualité générée par Ollama" if success else "Critères de qualité non satisfaits"
        )
        
        self.test_results.append(("Qualité des réponses", success))
        return success
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        self.print_header("🚀 TESTS D'INTÉGRATION OLLAMA AVEC AGENT AGNO")
        
        print(f"\nAPI URL: {self.api_url}")
        print(f"Endpoint: {self.chatbot_endpoint}")
        print(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        # Exécuter les tests
        self.test_simple_question()
        self.test_technical_question()
        self.test_complex_question()
        self.test_response_quality()
        
        # Résumé final
        self.print_header("📊 RÉSUMÉ DES TESTS")
        
        passed = sum(1 for _, success in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success in self.test_results:
            status = "✅" if success else "❌"
            print(f"{status} {test_name}")
        
        print("\n" + "=" * 80)
        print(f"RÉSULTAT FINAL: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
        print("=" * 80)
        
        if passed == total:
            print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
            print("✅ L'intégration Ollama avec Agent Agno est 100% fonctionnelle")
            return True
        else:
            print(f"\n⚠️ {total - passed} TEST(S) ONT ÉCHOUÉ")
            print("❌ L'intégration nécessite des corrections")
            return False


def main():
    """Fonction principale"""
    tester = OllamaIntegrationTester()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()

