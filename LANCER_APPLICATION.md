# 🚀 LANCER L'APPLICATION FREEMOBILACHAT

## Commande de Lancement

```bash
cd C:\Users\ander\Desktop\FreeMobilaChat
streamlit run streamlit_app/pages/5_Classification_Mistral.py --server.port=8502
```

## Accès à l'Application

**URL**: http://localhost:8502

## Interface

- **Dashboard moderne** avec Material Design
- **3 modes de classification** : FAST / BALANCED / PRECISE
- **KPIs en temps réel**
- **Export multi-formats** (CSV, Excel, JSON)

## Fonctionnalités

1. **Upload & Nettoyage** des tweets
2. **Classification intelligente** multi-modèle
3. **Visualisations interactives**
4. **Export des résultats**

## Modes Disponibles

| Mode      | Modèles              | Temps  | Précision |
|-----------|---------------------|--------|-----------|
| FAST      | BERT + Rules        | ~20s   | 75%       |
| BALANCED  | BERT + Rules + Mistral (20%) | ~2min | 88% |
| PRECISE   | BERT + Mistral (100%) | ~10min | 95% |

---

**Version**: 4.1 Professional Edition  
**Status**: ✅ Prêt pour production  
**Date**: 2025-11-08

