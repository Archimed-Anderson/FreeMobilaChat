# Guide de Gestion de la Visibilité du Repository

## Pour Mettre le Repository en Privé

### Étapes sur GitHub

1. **Accéder aux paramètres**
   - Aller sur https://github.com/Archimed-Anderson/FreeMobilaChat
   - Cliquer sur **"Settings"** (dans le menu horizontal)

2. **Changer la visibilité**
   - Scroller jusqu'en bas de la page
   - Dans la section **"Danger Zone"**
   - Cliquer sur **"Change visibility"**
   - Sélectionner **"Make private"**
   - Taper `Archimed-Anderson/FreeMobilaChat` pour confirmer
   - Cliquer sur **"I understand, change repository visibility"**

### Impact sur Streamlit Cloud

**✅ AUCUN IMPACT !**

- L'application reste accessible : https://freemobilachat.streamlit.app
- Les déploiements automatiques continuent de fonctionner
- Les mises à jour via `git push` fonctionnent normalement

### Vérifier les Permissions Streamlit

1. Aller sur https://share.streamlit.io
2. Cliquer sur votre profil (icône en haut à droite)
3. **Settings** > **GitHub Connections**
4. Vérifier que "Private repositories" est activé

Si ce n'est pas le cas :
- Cliquer sur **"Reconnect GitHub"**
- Autoriser l'accès aux repositories privés

---

## Pour Rendre le Repository Public (Après Soutenance)

### Étapes

1. Aller dans **Settings** du repository
2. Scroller jusqu'à **"Danger Zone"**
3. Cliquer sur **"Change visibility"**
4. Sélectionner **"Make public"**
5. Confirmer

### Avant de Rendre Public

**Checklist de Sécurité :**

- [ ] Vérifier qu'aucune clé API n'est dans le code
- [ ] Vérifier le fichier `.streamlit/secrets.toml` (doit être dans `.gitignore`)
- [ ] Vérifier qu'aucun mot de passe n'est présent
- [ ] Vérifier qu'aucune information sensible n'est dans les commits
- [ ] Relire le README pour information personnelle sensible

---

## Recommandations pour le Mémoire

### Stratégie Conseillée

**Phase 1 : Avant Soutenance (Maintenant)**
- Repository : **PRIVÉ**
- Application : **PUBLIQUE** (Streamlit Cloud)
- Raison : Protéger votre travail, éviter le plagiat

**Phase 2 : Pendant la Soutenance**
- Montrer l'application déployée
- Partager le lien GitHub au jury (les inviter comme collaborateurs si nécessaire)

**Phase 3 : Après Validation**
- Repository : **PUBLIC**
- Raison : Portfolio, CV, contribution open source

### Inviter le Jury (Si Repository Privé)

Si vous devez donner accès au jury :

1. **Settings** > **Collaborators**
2. Cliquer sur **"Add people"**
3. Entrer l'email ou nom d'utilisateur GitHub du membre du jury
4. Sélectionner le niveau d'accès : **"Read"** (lecture seule)

---

## Questions Fréquentes

### Q : L'application Streamlit Cloud restera-t-elle accessible si je mets le repo en privé ?

**R : OUI**, absolument. Streamlit Cloud a déjà l'autorisation d'accéder à vos repositories privés.

### Q : Puis-je changer la visibilité plusieurs fois ?

**R : OUI**, vous pouvez passer de public à privé et vice versa autant de fois que nécessaire.

### Q : Mes commits précédents restent-ils privés ?

**R : OUI**, tout l'historique devient privé. Attention : si quelqu'un a forké votre repo quand il était public, ce fork restera public.

### Q : Le lien Streamlit Cloud change-t-il ?

**R : NON**, l'URL reste la même : https://freemobilachat.streamlit.app

### Q : Les déploiements automatiques continuent-ils ?

**R : OUI**, chaque `git push` déclenche toujours un nouveau déploiement.

---

## Statut Actuel

- **Repository GitHub** : Public
- **Application Streamlit** : https://freemobilachat.streamlit.app (Public)
- **Recommandation** : Mettre en privé avant la soutenance

---

**Dernière mise à jour** : 21 octobre 2024

