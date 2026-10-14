# Suivi des intégrations Gladys

**Qui fait quoi ?** La [liste des intégrations Home Assistant](https://gist.github.com/Pierre-Gilles/9c4ba77a0faa47c4ea67c74351db9094)
de Pierre-Gilles, en face des intégrations externes Gladys qui existent déjà : publiées au store, en cours sur GitHub,
ou annoncées sur le forum. Pour éviter de développer deux fois la même chose.

👉 **https://william-de71.github.io/gladys-integrations-tracker/**

La page est reconstruite automatiquement toutes les 6 heures. On peut aussi télécharger les données :
[classeur .xlsx](https://william-de71.github.io/gladys-integrations-tracker/suivi-integrations-gladys.xlsx),
[CSV de la liste HA](https://william-de71.github.io/gladys-integrations-tracker/liste-ha-gladys.csv),
[CSV des intégrations Gladys](https://william-de71.github.io/gladys-integrations-tracker/integrations-gladys.csv).

## Tu veux prendre une intégration ?

1. Vérifie sur la page qu'elle est **libre**, et qu'elle n'apparaît pas déjà dans l'onglet « Intégrations Gladys ».
2. **Crée ton dépôt GitHub dès le premier jour**, même vide, avec le topic `gladys-assistant-integration`.
   C'est ce qui revendique l'intégration : elle apparaît ici comme « en cours » à la mise à jour suivante,
   sans rien remplir d'autre.
3. Annonce-la sur le [fil du forum](https://community.gladysassistant.com/t/10385).

## Statuts

| Statut | Signification |
|---|---|
| Publiée (store) | indexée par le [store Gladys](https://gladysassistant.com/fr/docs/integrations/external/) |
| Dépôt GitHub, pas encore au store | dépôt avec le topic, pas encore indexé (en cours, ou refusé par l'indexeur) |
| Dépôt GitHub sans topic store | dépôt repéré à la main sans le topic : en cours, ou topic oublié |
| Revendiquée (forum) | annoncée sur le forum, aucun dépôt trouvé |
| Libre | personne dessus à notre connaissance |

Une idée avec plusieurs dépôts est marquée **doublon**.

## D'où viennent les données

`build.py` relit à chaque exécution :

- le CSV du gist de Pierre-Gilles (`3_full-list.csv`) ;
- l'index du store : `https://integration-store-storage.gladysassistant.com/index.json` (nom, version, cover) ;
- les dépôts GitHub qui ont le topic [`gladys-assistant-integration`](https://github.com/topics/gladys-assistant-integration).

Trois fichiers sont tenus à la main, dans `data/` :

| Fichier | Contenu | Format |
|---|---|---|
| `mapping.txt` | correspondance entre une idée de la liste et un dépôt Gladys | `N° HA \| propriétaire/dépôt \| E` (équivalente) ou `P` (partielle) |
| `claims.txt` | intégrations annoncées sur le forum, sans dépôt | `N° HA \| qui \| source` |
| `extra-repos.txt` | dépôts Gladys qui n'ont pas le topic | `propriétaire/dépôt` |

Le rapprochement n'est pas automatique : un nouveau dépôt apparaît d'abord dans l'onglet « Intégrations Gladys »
avec la mention « hors liste ». **Une correspondance manque ou est fausse ? Ouvre une pull request sur `data/mapping.txt`.**

« Hors liste » est normal pour beaucoup d'intégrations : la liste a retiré ce que Gladys couvrait déjà
(Philips Hue, Sonos, Netatmo…), et certaines n'existent pas chez Home Assistant.

## Lancer en local

```sh
pip install -r requirements.txt
gh auth login          # le script interroge l'API GitHub via gh
python3 build.py       # écrit site/ : index.html, data.json, CSV, xlsx
python3 -m http.server -d site 8000
```

## Mise en place (une seule fois)

Dans les réglages du dépôt : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
Le workflow `build.yml` tourne ensuite toutes les 6 heures, à chaque push sur `data/`, `build.py` ou `index.html`,
et à la demande (onglet Actions → *Build and publish* → *Run workflow*).

GitHub met en pause les workflows planifiés d'un dépôt sans commit depuis 60 jours : il suffit alors de le
réactiver dans l'onglet Actions.

---

## English

Tracks which integrations from Pierre-Gilles' Home Assistant list already exist for Gladys (in the store, in progress
on GitHub, or claimed on the forum), so that two developers don't build the same one. Rebuilt every 6 hours from the
store index, the `gladys-assistant-integration` GitHub topic and the list. To claim an integration, create your
repository on day one with that topic. To fix a match, open a pull request on `data/mapping.txt`.
