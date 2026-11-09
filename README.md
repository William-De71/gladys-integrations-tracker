# Suivi des intégrations Gladys

**Qui fait quoi ?** Les listes d'intégrations de Pierre-Gilles ([octobre](https://gist.github.com/Pierre-Gilles/9c4ba77a0faa47c4ea67c74351db9094),
[novembre](https://gist.github.com/Pierre-Gilles/e02f7eda1e398401e0a9468a73d085fe)), en face des intégrations externes Gladys qui existent déjà : publiées au store, en cours sur GitHub,
ou annoncées sur le forum. Pour éviter de développer deux fois la même chose.

👉 **https://william-de71.github.io/gladys-integrations-tracker/**

La page est reconstruite automatiquement toutes les 30 minutes, et peut être
[mise à jour à la main](#mettre-à-jour-à-la-main) à tout moment. On peut aussi télécharger les données :
[classeur .xlsx](https://william-de71.github.io/gladys-integrations-tracker/suivi-integrations-gladys.xlsx),
[CSV de la liste HA](https://william-de71.github.io/gladys-integrations-tracker/liste-ha-gladys.csv),
[CSV des intégrations Gladys](https://william-de71.github.io/gladys-integrations-tracker/integrations-gladys.csv).

## Tu veux prendre une intégration ?

1. Vérifie sur la page qu'elle est **libre**, et qu'elle n'apparaît pas déjà dans l'onglet « Intégrations Gladys ».
2. **Crée ton dépôt dès le premier jour**, depuis le template
   [`integration-template-js`](https://github.com/GladysAssistant/integration-template-js) (bouton « Use this template »),
   avec un nom qui commence par `gladys-`, et **sans** le topic `gladys-assistant-integration`.
   C'est ce qui revendique l'intégration : le manifeste du template suffit pour qu'elle apparaisse ici « en cours »
   à la mise à jour suivante.
3. Annonce-la sur le [fil du forum](https://community.gladysassistant.com/t/10385).
4. **À la publication seulement**, ajoute le topic `gladys-assistant-integration` : c'est lui qui la fait entrer au store.
   Le poser plus tôt ferait apparaître une intégration vide dans le store.

Sans le template, le topic `gladys-integration-wip` fait le même effet : le store l'ignore, la page le repère.

## Les trois sources de la liste

- **La liste d'octobre de Pierre-Gilles** (idées n° 1 à 1190), lue dans son gist à chaque mise à jour. Elle ne contient que ce
  que Gladys ne couvrait pas encore le 12 octobre 2026.
- **L'analyse forum de juillet** (entrées F1, F2…, en tête de liste) : les intégrations Home Assistant populaires du
  [premier message du fil](https://community.gladysassistant.com/t/10385/1) que la liste a retirées parce que Gladys
  les couvrait déjà, en natif (MQTT, Matter, Google Cast…) ou par une intégration du store (Philips Hue, Sonos,
  Shelly…). Elles sont figées dans `data/ha-forum-juillet.csv`, numérotées par usage décroissant. Sans elles, ces
  intégrations Gladys apparaissaient « hors liste ».
- **La liste de novembre de Pierre-Gilles** (entrées N1 à N1000, en fin de liste), lue dans son
  [second gist](https://gist.github.com/Pierre-Gilles/e02f7eda1e398401e0a9468a73d085fe) à chaque mise à jour. Une
  entrée qui reprend une idée déjà présente (même identifiant Home Assistant, ou même nom) est fusionnée avec elle :
  l'idée garde son numéro d'octobre, et affiche « Aussi dans la liste de novembre : N12 (P1) ». Les autres deviennent
  des idées N1, N2… Les numéros N servent sur le forum comme les autres (« n° N12 »), même fusionnés. La liste de
  novembre ajoute le type d'intégration Gladys (appareils, fournisseur IA, synthèse vocale, calendrier…) et les pays,
  filtrables sur la page, ainsi que là où l'idée a été repérée (HA, HACS, ioBroker, Homey, Jeedom…). Son catalogue de contrats
  d'énergie (`energy-contracts-catalogue-candidates.csv`) n'est pas repris : ce ne sont pas des intégrations.

Les tuiles P1 à P4 restent calculées sur la liste d'octobre, pour rester comparables aux chiffres de Pierre-Gilles ;
la liste de novembre (avec ses idées fusionnées, et ses propres priorités P1 à P3) et l'analyse de juillet ont leurs
propres tuiles.

## Statuts

| Statut | Signification |
|---|---|
| Publiée (store) | indexée par le [store Gladys](https://gladysassistant.com/fr/docs/integrations/external/) |
| Native Gladys | couverte par le cœur de Gladys, sans intégration externe (entrées F de l'analyse de juillet) |
| Topic store posé, pas encore indexée | dépôt avec le topic du store, pas encore indexé (ou refusé par l'indexeur) |
| En cours (dépôt GitHub) | dépôt créé depuis le template, ou avec le topic `gladys-integration-wip` |
| Hors store, inactive | dépôt hors store sans commit depuis plus de 30 jours : l'intégration existe et compte pour l'idée, sauf si c'est une copie du template jamais remplie |
| Archivée, dépréciée ou supprimée | dépôt archivé ou supprimé sur GitHub, ou dont la description commence par « Deprecated » (ou « Obsolète », « Déprécié »), même si le store le liste encore : ne compte plus pour l'idée |
| Annoncée sur le forum | « je prends … » sur le [fil du forum](https://community.gladysassistant.com/t/10385), sans dépôt pour l'instant ; l'annonce expire au bout de 30 jours |
| Libre | personne dessus à notre connaissance |

Une idée avec plusieurs dépôts, ou deux intégrations Gladys du même nom, sont marquées **doublon**.

## Tout est automatique

Toutes les 30 minutes, `build.py` relit tout, sans rien à tenir à jour à la main :

- les listes de Pierre-Gilles : les CSV de ses gists (`3_full-list.csv` en octobre, `gladys-next-1000-integrations.csv`
  en novembre) ;
- le store : `https://integration-store-storage.gladysassistant.com/index.json` (nom, version, cover) ;
- les dépôts GitHub qui ont le topic [`gladys-assistant-integration`](https://github.com/topics/gladys-assistant-integration) ;
- les dépôts GitHub nommés « gladys… » qui contiennent un manifeste `gladys-assistant-integration.json` :
  c'est le cas de tout dépôt créé depuis le template, ce qui permet de revendiquer une intégration dès le premier jour ;
- les dépôts GitHub qui ont le topic `gladys-integration-wip`, même vides.

Le rapprochement est automatique aussi : une intégration Gladys est reliée à l'idée de la liste qui porte le même nom
(aux espaces près, « rtl433 » pour « rtl_433 », et sans le nom de domaine, « Healthchecks » pour « Healthchecks.io »),
ou dont le nom de dépôt reprend l'identifiant de l'intégration Home Assistant (`gladys-bosch-shc` pour `bosch_shc`,
quand cet identifiant fait au moins deux mots).
Une idée nommée « A / B » compte aussi sous chacun de ses noms (« La Poste / Colissimo / Chronopost tracking » sous
« La Poste »), sauf quand l'un d'eux est déjà une autre idée de la liste ou revient dans plusieurs idées.
La règle est stricte exprès, parce qu'une fausse correspondance serait pire qu'une correspondance manquante : ce qui ne
porte pas le même nom apparaît dans l'onglet « Intégrations Gladys » avec la mention « hors liste », et reste trouvable
par la recherche. Les **doublons** sont repérés automatiquement : deux intégrations Gladys qui portent le même nom, ou
qui correspondent à la même idée de la liste.

« Hors liste » est normal pour beaucoup d'intégrations : la liste a retiré ce que Gladys couvrait déjà
(Philips Hue, Sonos, Netatmo…), et certaines n'existent pas chez Home Assistant.

Les annonces du [fil du forum](https://community.gladysassistant.com/t/10385) sont lues aussi, dans le texte qui
suit « je prends » (ou « je m'occupe de », « je pars sur »…), jusqu'à la phrase suivante qui dit que l'idée appartient
à quelqu'un d'autre (« reste chez », « pris par »…) :
- les **numéros de la liste** cités (« Victron Energy GX (P1 n° 74) », « n° F39 » pour l'analyse de juillet, « n° N12 » pour la liste de novembre) sont le signal le plus sûr : quand une annonce
  en contient, seuls eux comptent, car ses descriptions citent souvent d'autres idées (« ça couvre Tasmota,
  BTHome… ») ;
- sinon, les noms de la liste écrits en entier, le plus long l'emportant quand deux se recouvrent (« Octopus Energy
  France » plutôt qu'« Octopus Energy »). Un nom raccourci (« Solcast » pour « Solcast PV Forecast ») n'est pas lu :
  `data/claims.txt` rattrape ces cas.

**Astuce pour réserver : citez le numéro de la liste**, comme « Solcast PV Forecast (n° 41) » ou « Piper TTS (n° N1) ».

Les messages de bilan de Pierre-Gilles et les citations sont ignorés. Chaque annonce renvoie vers son message, pour
vérifier d'un clic, et s'efface d'elle-même au bout de 30 jours sans dépôt. Dès qu'un dépôt existe, c'est lui qui fait foi.

### Corrections facultatives

Rien n'est obligatoire, mais quelques fichiers de `data/` permettent d'affiner :

| Fichier | Usage | Format |
|---|---|---|
| `mapping.txt` | relier une idée (n° de la liste, F de l'analyse de juillet ou N de la liste de novembre) et un dépôt aux noms différents, ou retirer une fausse correspondance automatique | `N° \| propriétaire/dépôt \| E` (équivalente), `P` (partielle) ou `-` (fausse) |
| `claims.txt` | signaler une annonce que la lecture du forum a manquée, ou libérer une idée abandonnée par son auteur (`-` à la place de qui : les annonces du forum et le statut du gist ne comptent plus) | `N° \| qui \| source` |
| `notes.txt` | afficher un avertissement sous une idée (conditions d'utilisation, accès restreint), en français et en anglais | `N° \| texte FR \| texte EN` |
| `bluetooth.txt` | corriger le repérage des idées Bluetooth (automatique : « Bluetooth » ou « BLE » dans le nom ou la description), utilisé par le filtre Bluetooth | `N° \| oui ou non` |
| `merge.txt` | corriger la fusion de la liste de novembre : rattacher une entrée N à une idée existante, ou la garder à part (`-`) | `N… \| n° de l'idée` ou `-` |
| `extra-repos.txt` | ajouter un dépôt que les recherches ne trouvent pas | `propriétaire/dépôt` |

Un push sur ces fichiers relance la page tout de suite, sans attendre la mise à jour suivante.

## Mettre à jour à la main

Sans attendre le passage suivant, deux façons :

- sur GitHub : onglet [Actions → Build and publish](https://github.com/William-De71/gladys-integrations-tracker/actions/workflows/build.yml)
  → bouton **Run workflow** (le bouton « Mettre à jour » en haut de la page y mène) ;
- en ligne de commande : `gh workflow run build.yml -R William-De71/gladys-integrations-tracker`.

La page est à jour environ une minute plus tard. Il faut les droits d'écriture sur le dépôt : un contributeur qui
n'en a pas peut demander une mise à jour sur le forum, ou attendre le passage suivant.

## Lancer en local

```sh
pip install -r requirements.txt
gh auth login          # le script interroge l'API GitHub via gh
python3 build.py       # écrit site/ : index.html, data.json, CSV, xlsx
python3 -m http.server -d site 8000
```

## Mise en place (une seule fois)

Dans les réglages du dépôt : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
Le workflow `build.yml` tourne ensuite toutes les 30 minutes, à chaque push sur `data/`, `build.py` ou `index.html`,
et à la demande (onglet Actions → *Build and publish* → *Run workflow*). Il se réactive lui-même à chaque passage,
pour que GitHub ne suspende pas la tâche planifiée faute d'activité sur le dépôt.

GitHub ne garantit pas l'heure des tâches planifiées : quand ses serveurs sont chargés, il les retarde, et en saute
parfois. Le workflow tourne donc à des minutes peu demandées (:07, :37), et la page affiche l'heure de sa
dernière mise à jour : au-delà de 75 minutes, elle le signale en rouge, et le bouton « Mettre à jour » rattrape le retard.

---

## English

Tracks which integrations from Pierre-Gilles' lists (October, and November as N1…N1000, merged with the October ideas it repeats) already exist for Gladys (in the store, in progress
on GitHub, or claimed on the forum), so that two developers don't build the same one. Rebuilt every 6 hours from the
store index, GitHub (the `gladys-assistant-integration` topic and repositories holding a Gladys manifest) and the list. To claim an integration, create your
repository on day one from the integration template, without the store topic (or with the
`gladys-integration-wip` topic), and add `gladys-assistant-integration` only when you publish. Updates also run on
demand: Actions → Build and publish → Run workflow. Discovery, matching and duplicate detection are automatic; `data/` only holds
optional corrections.
