# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Rédigé par :** GHZAOUNI Adam  ·  **Groupe :** G1-  ·  **Date :** 27/11/2026

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Pour chaque requête volontairement incorrecte, nous avons noté le code attendu avant de l'envoyer, puis le code réellement renvoyé dans `/docs` :

| Requête | Problème | Code prévu | Code obtenu |
|---|---|---:|---:|
| `POST /v1/predict` sans `load_pct` | champ obligatoire absent | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: 500` | valeur en dehors des bornes | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: "chaud"` | chaîne à la place d'un nombre | 422 | 422 |
| `POST /v1/predict` avec le champ `unknown` | champ non prévu par le schéma | 422 | 422 |
| `POST /v1/inconnue` | route inexistante | 404 | 404 |

**Une des prévisions s'est-elle révélée fausse ?**

Aucune. L'API a rejeté chaque donnée invalide avec un 422 et a répondu 404 pour la route qui n'existe pas, exactement comme anticipé.

Résultat de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
2 failed, 16 passed in 13.98s
```

**À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il ?**

Ce décorateur permet d'exécuter une même fonction de test sur plusieurs jeux d'entrées. Comme nous lui avons fourni cinq cas, pytest lance la fonction cinq fois et comptabilise cinq tests distincts, chacun pouvant réussir ou échouer indépendamment.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
UP017 [*] Use `datetime.UTC` alias
--> maintai\train.py:58:36
Found 1 error.
[*] 1 fixable with the `--fix` option.
```

**Quelle différence entre `ruff check .` et `python -m pytest` ?**

Ruff analyse le code sans l'exécuter : il signale les erreurs de syntaxe, les imports inutiles, les écarts de style et les mauvaises pratiques. Pytest, au contraire, exécute le code au travers des tests pour vérifier que l'application produit bien les résultats attendus. L'un juge la forme du code, l'autre son comportement.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Résultat de `python -m pytest` juste après la mise en place :

```
===================================== 2 failed, 16 passed, 1 warning in 3.82s =====================================
```

**Quels tests échouent, et que reçoivent-ils à la place de 401 ?**

Il s'agit de `test_missing_key_is_rejected` et `test_wrong_key_is_rejected`. Ils obtiennent un 200 au lieu du 401 attendu, puisque l'API n'a encore aucune protection et accepte n'importe quelle requête.

## 4. La clé API (sprint 1)

Fonction `require_api_key()` (`maintai/api/security.py`) :

```python
    cle_attendue = get_settings().api_key

    if cle_attendue is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La clé API n'est pas configurée sur le serveur",
        )

    if x_api_key is None or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
```

Déclaration du `router` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

**Après avoir écrit `security.py` sans modifier le router, combien de tests échouent ?**

Toujours deux. La fonction de vérification existe, mais aucune route ne l'utilise encore : tant qu'elle n'est pas branchée sur le router via `dependencies=[Depends(require_api_key)]`, elle n'est jamais appelée.

Résultat de `python -m pytest` à la fin du sprint 1 :

```
========================================== 18 passed, 1 warning in 3.59s ==========================================
```

Requêtes envoyées après `uvicorn maintai.api.main:app --reload --env-file .env` :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-11-02T17:33:13Z"}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150}}]}` |

**Pourquoi 500 °C donne-t-il 401 sans clé et 422 avec la clé ?**

Tout dépend de l'ordre des vérifications. L'authentification passe en premier : sans clé valide, l'API s'arrête immédiatement avec un 401, sans même lire le corps de la requête. Une fois la clé acceptée, le corps est validé par Pydantic, et c'est seulement là que la température de 500 °C (au-delà de la limite de 150 °C) est détectée, d'où le 422.

**Sans `--env-file .env`, quel code obtient-on avec la clé, et pourquoi pas 401 ?**

On obtient un 500. Sans le fichier `.env`, la variable `MAINTAI_API_KEY` n'est pas définie et `get_settings().api_key` vaut `None`. Notre fonction traite ce cas en premier et renvoie une erreur serveur. C'est logique : la faute ne vient pas du client, mais d'un serveur mal configuré. Un 401 signifierait que la clé envoyée est mauvaise, alors qu'ici elle n'est même pas comparée, faute de valeur de référence.

## 5. La page web (sprint 2)

Contenu du `addEventListener` dans `web/index.html` :

```javascript
const reading = Object.fromEntries(FEATURES.map(f => [f, Number(document.getElementById(f).value)]));
  const url = document.getElementById("url").value;
  const key = document.getElementById("key").value;
  try {
    const res = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": key },
      body: JSON.stringify(reading),
    });
    const data = await res.json();
    if (!res.ok) {
      show("err", `Erreur ${res.status} : ${JSON.stringify(data.detail)}`);
      return;
    }
    const pct = (data.failure_probability * 100).toFixed(1);
    show(data.alert ? "alert" : "ok", `Probabilité de panne : ${pct} % (${data.alert ? "ALERTE" : "OK"})`);
  } catch (e) {
    show("err", `Impossible de joindre l'API : ${e.message}`);
  }
```

Affichage de la page servie sur le port 5500 :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | Probabilité de panne : 94.8 % (ALERTE) |
| 500 °C, bonne clé | Erreur 422 : [{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150}}] |
| relevé normal, fausse clé | Erreur 401 : "Clé API absente ou invalide" |

**Expérience CORS : page servie sur le port 5501.**

La page indique « Impossible de joindre l'API : Failed to fetch ». Dans la console (F12), le navigateur explique que la requête vers `http://localhost:8000/v1/predict` depuis l'origine `http://localhost:5501` a été bloquée par la politique CORS, car la réponse ne contient pas d'en-tête `Access-Control-Allow-Origin`.

La raison : seule l'origine du port 5500 figure dans `MAINTAI_CORS_ORIGINS`. Pour le port 5501, l'API ne renvoie pas l'en-tête d'autorisation et le navigateur refuse de transmettre la réponse à la page.

**Pourquoi `curl.exe` reçoit-il une réponse alors que la page du port 5501 est bloquée ?**

Le contrôle CORS est fait par le navigateur, pas par le serveur. Le serveur traite bien la requête ; c'est le navigateur qui décide de ne pas livrer la réponse à une page dont l'origine n'est pas autorisée. `curl.exe` n'étant pas un navigateur, il ne connaît pas la notion d'origine et ne tient pas compte de l'en-tête `Access-Control-Allow-Origin`.

## 6. Les tests de l'activité 1 dans le TP2

**Sans `headers=HEADERS`, combien de tests de `test_casser.py` échouent, et lequel passe malgré tout ?**

Les quatre cas qui ciblent `/v1/predict` échouent avec un 401 : la clé est contrôlée avant les données, donc l'erreur de validation attendue n'est jamais atteinte. Seul le cas de la route inexistante passe, avec son 404 : comme aucune route ne correspond, la dépendance d'authentification n'est jamais exécutée.

Résultat de `python -m pytest` avec `headers=HEADERS` :

```
============================= 23 passed in 4.36s ==============================
```

## 7. Questions de compréhension

**1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?**

- **401 Unauthorized** : le client n'est pas authentifié, sa clé est absente ou fausse.
- **422 Unprocessable Entity** : la requête est arrivée et le client est reconnu, mais le contenu envoyé ne passe pas la validation.
- **403 Forbidden** : le client est bien identifié, mais il n'a pas le droit d'accéder à cette ressource.

En résumé, 401 répond à « qui es-tu ? », 403 à « as-tu le droit ? » et 422 à « tes données sont-elles correctes ? ».

**2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example` ?**

La clé est un secret : écrite dans le code ou poussée sur GitHub, elle deviendrait lisible par n'importe qui ayant accès au dépôt. Le fichier `.env` contient les vraies valeurs, dont la clé, et reste exclu de Git grâce au `.gitignore`. Le fichier `.env.example` sert de modèle : il liste les variables nécessaires avec des valeurs fictives. C'est uniquement lui qui est commité.

**3. Pourquoi la clé passe-t-elle dans un en-tête et non dans l'URL ?**

Une URL laisse beaucoup de traces : historique du navigateur, journaux du serveur et des proxys, outils d'analyse. En plaçant la clé dans l'en-tête `X-API-Key`, on évite de l'exposer à tous ces endroits. Pour qu'elle soit réellement protégée pendant le transport, il faut en plus utiliser HTTPS.

**4. Qu'apporte `secrets.compare_digest` par rapport à `==` ?**

Une comparaison avec `==` s'arrête au premier caractère différent, si bien que sa durée varie selon le nombre de caractères corrects. Un attaquant pourrait exploiter ces écarts de temps pour deviner la clé petit à petit (attaque temporelle). `secrets.compare_digest` compare les chaînes en un temps qui ne dépend pas de leur contenu, ce qui supprime cette fuite d'information.

**5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même ?**

Une origine est le triplet protocole + hôte + port. Ici, le protocole et l'hôte sont identiques mais les ports diffèrent : ce sont donc deux origines distinctes. C'est pourquoi le navigateur applique la politique CORS et vérifie que l'API autorise bien l'origine de la page.

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp2` existe sur GitHub : oui
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non
- Relecture de la pull request : RIZQY Nabila

## 9. Ce qui reste flou

Les notions centrales du TP sont acquises : validation des données avec Pydantic, protection de l'API par clé, signification des codes HTTP et fonctionnement de CORS.
