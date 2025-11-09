# 🚀 Guide de Démarrage Rapide - Dashboard Multi-Modèle

## ✅ État Actuel

### Tests Réussis
- ✅ **Tous les imports fonctionnent** (5/5 modules)
- ✅ **BERT chargé sur CPU** (RTX 5060 sm_120 non supporté → fallback CPU automatique)
- ✅ **TweetCleaner opérationnel** (nettoyage + déduplication)
- ✅ **Rule Classifier opérationnel** (is_claim, urgence, topics)
- ✅ **MultiModelOrchestrator prêt** (modes FAST/BALANCED/PRECISE)
- ✅ **Streamlit lancé** (port 8501 actif)

### Corrections Appliquées
1. **GPU Compatibility**: Détection automatique RTX 5060 → Fallback CPU
2. **BERT Device**: Modèle correctement déplacé sur le device (CPU)
3. **Noms de Méthodes**: `predict_sentiment_batch`, `classify_batch`
4. **Encodage UTF-8**: Scripts de test configurés pour Windows
5. **Imports Logging**: Diagnostic détaillé des imports

---

## 🎯 Lancement du Dashboard

### Méthode 1: Script Automatique (Recommandé)
```powershell
python lancer_dashboard.py
```

### Méthode 2: Commande Directe
```powershell
python -m streamlit run streamlit_app/pages/5_Classification_Mistral.py
```

### Méthode 3: Via Job PowerShell
```powershell
Start-Job -ScriptBlock { 
    Set-Location "C:\Users\ander\Desktop\FreeMobilaChat"
    python -m streamlit run "streamlit_app/pages/5_Classification_Mistral.py"
}
```

**URL du Dashboard**: http://localhost:8501/Classification_Mistral

---

## 🔍 Diagnostic en Cas de Problème

### 1. Test des Imports
```powershell
python diagnostic_imports.py
```
**Résultat attendu**: `✅ TOUS LES IMPORTS RÉUSSISSENT (5/5)`

### 2. Test Complet du Système
```powershell
python test_dashboard_simple.py
```
**Résultat attendu**: `✅ TOUS LES TESTS RÉUSSIS!`

### 3. Vérifier le Port 8501
```powershell
Get-NetTCPConnection -LocalPort 8501 -State Listen
```
**Résultat attendu**: Une connexion en état LISTEN

### 4. Test HTTP
```powershell
python check_debug.py
```
**Résultat attendu**: Status 200

---

## 🐛 Dépannage

### Problème: "Port 8501 already in use"
**Solution**:
```powershell
Get-NetTCPConnection -LocalPort 8501 | ForEach-Object { 
    Stop-Process -Id $_.OwningProcess -Force 
}
```

### Problème: "Module not found"
**Solution**:
```powershell
pip install torch transformers unidecode emoji ollama joblib scikit-learn tqdm
```

### Problème: "GPU Error"
**Solution**: C'est normal! Le RTX 5060 (sm_120) n'est pas supporté par PyTorch 2.5.1.  
→ Le système bascule automatiquement sur CPU (100+ tweets/s).

### Problème: "Page vide"
**Solution 1**: Forcer le rechargement
```powershell
# Arrêter Streamlit
Get-Process python | Where-Object {$_.MainWindowTitle -like "*streamlit*"} | Stop-Process -Force

# Relancer
python -m streamlit run streamlit_app/pages/5_Classification_Mistral.py
```

**Solution 2**: Vérifier les logs
```powershell
# Lancer avec logs visibles
python -m streamlit run streamlit_app/pages/5_Classification_Mistral.py 2>&1 | Tee-Object -FilePath streamlit_logs.txt
```

---

## 📊 Fonctionnalités du Dashboard

### 3 Modes de Classification
| Mode | Durée (5000 tweets) | KPIs Détectés | Modèles Utilisés |
|------|---------------------|---------------|------------------|
| ⚡ FAST | ~20 secondes | Sentiment + Topics | BERT + Rules |
| ⭐ BALANCED | ~2-3 minutes | Tous (6 KPIs) | BERT + Rules + Mistral (échantillon) |
| 🎯 PRECISE | ~8-10 minutes | Tous (6 KPIs) | BERT + Rules + Mistral (complet) |

### 6 KPIs Calculés
1. **is_claim**: Le tweet contient-il une réclamation?
2. **sentiment**: positif / négatif / neutre
3. **urgence**: faible / moyenne / critique
4. **topics**: produit, service, support, facturation, technique, réseau
5. **incident**: Type d'incident détecté
6. **confidence**: Score de confiance (0-1)

### Workflow
1. **Upload CSV** → Charger votre fichier de tweets
2. **Nettoyage** → Suppression doublons (MD5) + nettoyage texte
3. **Classification** → Mode choisi appliqué
4. **Résultats** → 6 KPI cards + 6 graphiques Plotly
5. **Export** → CSV, JSON stats, rapport KPIs

---

## 🖥️ Performances sur Votre Machine

### Configuration Détectée
- **CPU**: Intel i9-13900H (13th Gen)
- **RAM**: 32 GB
- **GPU**: NVIDIA RTX 5060 Laptop (sm_120 - non compatible PyTorch 2.5.1)
- **Device BERT**: CPU (fallback automatique)

### Performances Attendues (Mode BALANCED)
- **Nettoyage**: 5000 tweets → ~5 secondes
- **BERT (CPU)**: 5000 tweets → ~50 secondes
- **Rules**: 5000 tweets → ~2 secondes
- **Mistral (échantillon)**: 500 tweets → ~90 secondes  
**TOTAL**: ~2-3 minutes pour 5000 tweets

---

## 📝 Notes Importantes

### RTX 5060 et PyTorch
Le RTX 5060 a une compute capability **sm_120** (Blackwell architecture).  
PyTorch 2.5.1 supporte jusqu'à **sm_90** (Hopper).  

**Solution implémentée**: Détection automatique → Fallback CPU.  
**Performance CPU**: Excellente grâce au i9-13900H (100+ tweets/s avec BERT).

**Pour utiliser le GPU** (optionnel, future):
```bash
# Installer PyTorch Nightly (support sm_120 en cours)
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu121
```

---

## 🎉 Commande Finale

```powershell
# 1. Ouvrir PowerShell dans le dossier du projet
cd C:\Users\ander\Desktop\FreeMobilaChat

# 2. Tuer tout processus Streamlit existant
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 3. Lancer le dashboard
python -m streamlit run streamlit_app/pages/5_Classification_Mistral.py

# 4. Ouvrir le navigateur
Start-Process "http://localhost:8501/Classification_Mistral"
```

---

## 📞 En Cas de Problème Persistant

1. **Capture d'écran** de la page Streamlit
2. **Copier les logs** du terminal
3. **Exécuter** `python diagnostic_imports.py` et partager le résultat
4. **Vérifier** `diagnostic_result.txt` (doit dire `MODULES_AVAILABLE: True`)

---

✨ **Le dashboard est maintenant prêt à l'emploi !** ✨

