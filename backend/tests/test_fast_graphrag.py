"""
Tests pour le service Fast-GraphRAG
Vérifie la construction du graphe, la récupération de contexte et les mises à jour incrémentales
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.fast_graphrag_service import FastGraphRAGService
from app.config.fast_graphrag_config import FastGraphRAGConfig

# Documents de test sur Free Mobile
TEST_DOCUMENTS = [
    "Free Mobile propose des forfaits 4G et 5G avec data illimitée en France métropolitaine.",
    "Pour activer la 4G sur votre téléphone, allez dans Paramètres > Réseau mobile > Activer 4G.",
    "L'APN Free Mobile est: internet.free-mobile.fr pour l'internet et mms.orange.fr pour les MMS.",
    "Le forfait Free 5G coûte 19,99€/mois et inclut 210 Go de data en France et 25 Go en Europe.",
    "Pour contacter le service client Free Mobile, appelez le 3244 (gratuit depuis un mobile Free).",
    "La couverture réseau Free Mobile utilise les antennes Orange en itinérance.",
    "Pour configurer votre messagerie vocale, composez le 666 depuis votre mobile Free.",
    "Free Mobile propose une application mobile pour gérer votre compte et consommer votre forfait."
]

async def test_graph_construction():
    """Test 1: Construction du graphe à partir de documents"""
    print("\n" + "="*80)
    print("  TEST 1: CONSTRUCTION DU GRAPHE")
    print("="*80)
    
    try:
        # Créer une configuration de test
        config = FastGraphRAGConfig(
            storage_dir=Path("/app/data/fast_graphrag_test"),
            top_k_nodes=3
        )
        
        # Initialiser le service
        service = FastGraphRAGService(config)
        
        # Construire le graphe
        print(f"\n📦 Construction du graphe avec {len(TEST_DOCUMENTS)} documents...")
        success = await service.build_graph_from_documents(TEST_DOCUMENTS)
        
        if success:
            stats = service.get_graph_stats()
            print(f"\n Graphe construit avec succès:")
            print(f"   - Nœuds: {stats['num_nodes']}")
            print(f"   - Documents: {stats['num_documents']}")
            print(f"   - Stockage: {stats['storage_path']}")
            return True, service
        else:
            print("\n Échec de la construction du graphe")
            return False, None
            
    except Exception as e:
        print(f"\n ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_context_retrieval(service: FastGraphRAGService):
    """Test 2: Récupération de contexte avec différentes requêtes"""
    print("\n" + "="*80)
    print("  TEST 2: RÉCUPÉRATION DE CONTEXTE")
    print("="*80)
    
    test_queries = [
        "Comment activer la 4G ?",
        "Quel est le prix du forfait 5G ?",
        "Comment contacter le service client ?"
    ]
    
    all_success = True
    
    for query in test_queries:
        print(f"\n🔍 Requête: {query}")
        
        try:
            results = await service.query_graph(query, top_k=3)
            
            if results:
                print(f" Trouvé {len(results)} résultats:")
                for i, result in enumerate(results, 1):
                    print(f"\n   {i}. Score: {result['score']:.3f}")
                    print(f"      Contenu: {result['content'][:80]}...")
            else:
                print(" Aucun résultat trouvé")
                all_success = False
                
        except Exception as e:
            print(f" ERREUR: {e}")
            all_success = False
    
    return all_success

async def test_incremental_update(service: FastGraphRAGService):
    """Test 3: Mise à jour incrémentale du graphe"""
    print("\n" + "="*80)
    print("  TEST 3: MISE À JOUR INCRÉMENTALE")
    print("="*80)
    
    new_documents = [
        "Free Mobile propose également des options internationales pour appeler à l'étranger.",
        "Le roaming en Europe est inclus dans tous les forfaits Free Mobile."
    ]
    
    try:
        print(f"\n🔄 Ajout de {len(new_documents)} nouveaux documents...")
        
        stats_before = service.get_graph_stats()
        print(f"   Avant: {stats_before['num_documents']} documents")
        
        success = await service.update_graph(new_documents)
        
        if success:
            stats_after = service.get_graph_stats()
            print(f"   Après: {stats_after['num_documents']} documents")
            print(f"\n Mise à jour réussie (+{stats_after['num_documents'] - stats_before['num_documents']} documents)")
            return True
        else:
            print("\n Échec de la mise à jour")
            return False
            
    except Exception as e:
        print(f"\n ERREUR: {e}")
        return False

async def test_fallback_on_error():
    """Test 4: Test du fallback en cas d'erreur"""
    print("\n" + "="*80)
    print("  TEST 4: FALLBACK EN CAS D'ERREUR")
    print("="*80)
    
    try:
        # Créer une configuration avec fallback activé
        config = FastGraphRAGConfig(
            storage_dir=Path("/app/data/fast_graphrag_test"),
            enable_fallback=True,
            fallback_on_error=True
        )
        
        service = FastGraphRAGService(config)
        
        # Tester une requête même si le graphe n'est pas construit
        print("\n🔍 Test de requête sans graphe construit...")
        results = await service.query_graph("Test query", top_k=3)
        
        # Le service devrait retourner une liste vide sans erreur
        if isinstance(results, list):
            print(f" Fallback fonctionne: retour d'une liste vide ({len(results)} résultats)")
            return True
        else:
            print(" Fallback ne fonctionne pas correctement")
            return False
            
    except Exception as e:
        print(f" ERREUR: {e}")
        return False

async def main():
    """Exécuter tous les tests"""
    print("\n" + "="*80)
    print("   TESTS DU SERVICE FAST-GRAPHRAG")
    print("="*80)
    
    results = {
        "construction": False,
        "retrieval": False,
        "update": False,
        "fallback": False
    }
    
    # Test 1: Construction du graphe
    results["construction"], service = await test_graph_construction()
    
    # Test 2: Récupération de contexte (seulement si construction réussie)
    if results["construction"] and service:
        results["retrieval"] = await test_context_retrieval(service)
        
        # Test 3: Mise à jour incrémentale
        results["update"] = await test_incremental_update(service)
    
    # Test 4: Fallback (indépendant)
    results["fallback"] = await test_fallback_on_error()
    
    # Résumé
    print("\n" + "="*80)
    print("   RÉSUMÉ DES TESTS")
    print("="*80)
    
    test_names = {
        "construction": "Construction du graphe",
        "retrieval": "Récupération de contexte",
        "update": "Mise à jour incrémentale",
        "fallback": "Fallback en cas d'erreur"
    }
    
    for key, name in test_names.items():
        status = "" if results[key] else ""
        print(f"{status} {name}")
    
    # Résultat final
    total_tests = len(results)
    passed_tests = sum(results.values())
    success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "="*80)
    print(f"RÉSULTAT FINAL: {passed_tests}/{total_tests} tests réussis ({success_rate:.1f}%)")
    print("="*80)
    
    if passed_tests == total_tests:
        print("\n TOUS LES TESTS SONT PASSÉS !")
        print(" Le service Fast-GraphRAG est 100% fonctionnel")
    else:
        print(f"\n {total_tests - passed_tests} test(s) ont échoué")
        print(" Des corrections sont nécessaires")
    
    print()

if __name__ == "__main__":
    asyncio.run(main())

