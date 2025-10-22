# Guide : Déployer sur Streamlit Cloud avec Repository Privé

## Problème Rencontré

```
Failed to download the sources for repository
Make sure the repository and the branch exist and you have write access to it
```

## Solution : Configuration des Permissions

### Étape 1 : Vérifier sur GitHub

1. **Allez sur** : https://github.com/settings/installations

2. **Cherchez "Streamlit"** dans la liste des applications installées

3. **Cliquez sur "Configure"**

4. **Vérifiez "Repository access"** :
   - Option A : **"All repositories"** (recommandé)
   - Option B : **"Only select repositories"** → Cochez `FreeMobilaChat`

5. **Vérifiez les permissions** :
   - ✅ Read access to code
   - ✅ Read access to metadata
   - ✅ Read and write access to deployments

6. **Sauvegardez** les changements

---

### Étape 2 : Reconnexion sur Streamlit Cloud

1. **Allez sur** : https://share.streamlit.io

2. **Profil → Settings → Source control**

3. **Cliquez "Reconnect GitHub"**

4. **Autorisez l'accès** :
   - ✅ Private repositories
   - ✅ Archimed-Anderson account

---

### Étape 3 : Créer/Redéployer l'App

#### Si l'app existe déjà :
1. Menu "⋮" → **Delete app**
2. Attendez 30 secondes
3. Créez une nouvelle app

#### Configuration de la nouvelle app :
```
Repository: Archimed-Anderson/FreeMobilaChat
Branch: main
Main file path: streamlit_app/app.py
Python version: 3.11
Advanced settings: (optionnel pour secrets)
```

---

## Vérification : Repository Privé ou Public ?

### Pour vérifier le statut actuel :

1. Allez sur : https://github.com/Archimed-Anderson/FreeMobilaChat

2. Si vous voyez 🔒 **Private** en haut à droite → Repository privé

3. Si vous voyez 👁️ **Public** → Repository public

---

## Alternative : Rendre le Repository Public Temporairement

Si la configuration des permissions est trop complexe :

### Avantages de rendre le repo public :
- ✅ Déploiement immédiat sans configuration
- ✅ Pas de problème de permissions
- ✅ Bon pour portfolio académique
- ✅ Tous les fichiers sensibles sont déjà retirés

### Comment rendre public :

1. **Sur GitHub** : https://github.com/Archimed-Anderson/FreeMobilaChat

2. **Settings** (onglet du repository)

3. **Scroll jusqu'en bas** → Section "Danger Zone"

4. **"Change visibility"** → **"Make public"**

5. **Tapez le nom du repository** pour confirmer

6. **Retour sur Streamlit Cloud** → Redéployez

---

## Sécurité : Fichiers à NE JAMAIS Publier

✅ **Ces fichiers sont déjà protégés par .gitignore** :
- ❌ Fichiers .csv (données)
- ❌ Fichiers .db (bases de données)
- ❌ Fichiers .xlsx (données Excel)
- ❌ Fichiers .pkl (modèles)
- ❌ Secrets et API keys (.env, secrets.toml)

✅ **Vérification effectuée** :
Tous les fichiers sensibles ont été retirés du repository lors du fix précédent.

**Il n'y a AUCUN risque** à rendre le repository public maintenant.

---

## Dépannage

### Erreur : "Failed to clone"
→ Permissions GitHub insuffisantes
→ Solution : Suivre Étape 1 et 2 ci-dessus

### Erreur : "Main module does not exist"
→ Chemin incorrect
→ Solution : Utiliser `streamlit_app/app.py` (pas `app.py`)

### Erreur : "Repository not found"
→ Nom de repository incorrect
→ Solution : Vérifier `Archimed-Anderson/FreeMobilaChat`

---

## Contact Support Streamlit

Si le problème persiste après toutes ces étapes :

**Support Streamlit** : https://discuss.streamlit.io/
**Documentation** : https://docs.streamlit.io/streamlit-community-cloud/get-started

---

**Mis à jour** : 22 octobre 2024

