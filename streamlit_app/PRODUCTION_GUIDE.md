# Guide de Production FreeMobilaChat

## 🚀 Déploiement en Production

### 1. Tests Complets

Avant la mise en production, lancez tous les tests :

```bash
# Tests complets du système
python test_complete_system.py

# Tests d'intégration
python test_integration.py

# Vérification de la configuration
python run.py --check-config
```

### 2. Déploiement Automatique

```bash
# Déploiement complet en production
python deploy_production.py
```

### 3. Démarrage Manuel

```bash
# Démarrage de l'application
python run_production.py start

# Vérification du statut
python run_production.py status

# Affichage des logs
python run_production.py logs
```

## 📊 Monitoring et Maintenance

### Statut de l'Application

```bash
# Vérifier le statut
python run_production.py status

# Afficher les logs
python run_production.py logs 100

# Redémarrer l'application
python run_production.py restart
```

### Métriques de Performance

- **CPU** : < 80%
- **Mémoire** : < 85%
- **Disque** : < 90%
- **Temps de réponse** : < 3 secondes

### Logs et Debugging

```bash
# Logs en temps réel
tail -f logs/app.log

# Recherche d'erreurs
grep "ERROR" logs/app.log

# Statistiques des logs
wc -l logs/app.log
```

## 🔧 Configuration de Production

### Variables d'Environnement

```bash
# Configuration optimale
export STREAMLIT_ENV=production
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_ENABLE_CORS=true
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50MB
export STREAMLIT_SERVER_TIMEOUT=300
export STREAMLIT_LOGGER_LEVEL=INFO
```

### Configuration Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

## 🛡️ Sécurité

### Recommandations

1. **Firewall** : Limitez l'accès aux ports nécessaires
2. **HTTPS** : Utilisez SSL/TLS en production
3. **Authentification** : Ajoutez une authentification si nécessaire
4. **Validation** : Validez toutes les entrées utilisateur
5. **Logs** : Surveillez les logs pour détecter les anomalies

### Configuration Sécurisée

```bash
# Limitation des uploads
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10MB

# Désactivation des stats
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Timeout court
export STREAMLIT_SERVER_TIMEOUT=60
```

## 📈 Optimisation

### Performance

1. **Cache** : Utilisez le cache Streamlit
2. **Lazy Loading** : Chargez les données à la demande
3. **Compression** : Activez la compression gzip
4. **CDN** : Utilisez un CDN pour les assets statiques

### Monitoring

```bash
# Surveillance des ressources
htop
iostat -x 1
netstat -tulpn | grep :8501

# Surveillance de l'application
curl -f http://localhost:8501/health
```

## 🔄 Mise à Jour

### Processus de Mise à Jour

1. **Sauvegarde** : Sauvegardez les données importantes
2. **Tests** : Testez la nouvelle version
3. **Déploiement** : Déployez pendant une fenêtre de maintenance
4. **Vérification** : Vérifiez que tout fonctionne
5. **Rollback** : Préparez un plan de retour en arrière

### Commandes de Mise à Jour

```bash
# Arrêt de l'application
python run_production.py stop

# Sauvegarde
cp -r data/ data_backup_$(date +%Y%m%d_%H%M%S)/

# Mise à jour du code
git pull origin main

# Redémarrage
python run_production.py start
```

## 🆘 Dépannage

### Problèmes Courants

#### Application ne démarre pas

```bash
# Vérifier les logs
python run_production.py logs

# Vérifier les ports
netstat -tulpn | grep :8501

# Vérifier les permissions
ls -la logs/
```

#### Performance dégradée

```bash
# Vérifier les ressources
htop
df -h
free -h

# Redémarrer l'application
python run_production.py restart
```

#### Erreurs de connexion

```bash
# Vérifier le firewall
sudo ufw status

# Vérifier la configuration
python run_production.py status
```

### Logs d'Erreur

```bash
# Recherche d'erreurs
grep -i "error\|exception\|traceback" logs/app.log

# Erreurs récentes
tail -n 100 logs/app.log | grep -i "error"

# Statistiques des erreurs
grep -c "ERROR" logs/app.log
```

## 📞 Support

### Contact

- **Issues** : [GitHub Issues](https://github.com/freemobilachat/issues)
- **Email** : support@freemobilachat.com
- **Discord** : [Discord Server](https://discord.gg/freemobilachat)

### Informations de Debug

```bash
# Informations système
python -c "
import sys, platform
print(f'Python: {sys.version}')
print(f'OS: {platform.system()} {platform.release()}')
print(f'Architecture: {platform.machine()}')
"

# Modules installés
pip list | grep -E "(streamlit|pandas|plotly)"

# Configuration
python run_production.py status
```

---

**FreeMobilaChat** - Guide de production complet 🚀
