# V2X Communication Simulator (SUMO + Python)

Projet académique pour simuler la communication V2X entre un VRU (piéton/cycliste)
et un véhicule, avec deux modes de communication : direct ou via RSU.

## Etat actuel du projet

- Scenario SUMO minimal déterministe disponible (`veh_0` + `ped_0`).
- Pilotage SUMO pas à pas via TraCI implémenté.
- Construction d'un contexte de décision (`Context`) implémentée.
- Détection de proximité dangereuse (distance euclidienne + seuil) implémentée.
- Modèle de communication simplifié (direct / infrastructure) implémenté.
- Fonction de récompense temporelle (`compute_reward`) implémentée.
- Base de tests `pytest` en place et verte.

Ce qui reste à faire ensuite : brancher toute la chaîne dans une boucle unique
(TraCI -> context -> danger -> communication -> politique baseline/MAB).

## Structure du projet

- `v2x_sim/sumo_runner.py` : lance SUMO/SUMO-GUI via TraCI, fait `simulationStep()`, lit états véhicules/piétons.
- `v2x_sim/context_builder.py` : définit `Context` et construit un contexte décisionnel (distance, danger, rsu_available, rsu_load, obstacle_present).
- `v2x_sim/danger_detector.py` : fonctions pures de détection de danger + détecteur par paires VRU/véhicule.
- `v2x_sim/communication_model.py` : simulation paramétrable des communications directes et via RSU (`CommunicationResult`).
- `v2x_sim/reward.py` : fonction de récompense basée sur succès/échec et respect d'une deadline.
- `v2x_sim/baseline.py` : stratégies baseline (`AlwaysDirect`, `AlwaysInfrastructure`, `ThresholdHeuristic`) + interface commune.
- `v2x_sim/thompson.py` : squelette Thompson Sampling pour futur MAB.
- `v2x_sim/metrics.py` : collecte de métriques de simulation.
- `v2x_sim/main.py` : boucle de simulation complète (sans MAB) avec stratégie, communication, reward et résumé final.
- `scenarios/minimal_v2x/` : scénario SUMO minimal reproductible.
- `scenarios/rich_v2x/` : scénario SUMO plus riche (intersection, multi-véhicules, multi-VRU).
- `tests/` : tests unitaires `pytest`.

## Installation (Ubuntu)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-pytest
sudo apt install -y sumo sumo-tools sumo-doc
```

Vérification :

```bash
python3 --version
pytest --version
sumo --version
netconvert --version
```

Si `import traci` échoue côté Python, ajouter les outils SUMO au `PYTHONPATH` :

```bash
export PYTHONPATH="/usr/share/sumo/tools:${PYTHONPATH}"
```

## Scenario SUMO minimal

Dossier : `scenarios/minimal_v2x/`

Générer le réseau (si besoin) :

```bash
cd scenarios/minimal_v2x
bash generate_network.sh
```

Lancer SUMO directement :

```bash
sumo -c scenario.sumocfg
```

## Scenario SUMO riche

Dossier : `scenarios/rich_v2x/`

Générer le réseau :

```bash
cd scenarios/rich_v2x
bash generate_network.sh
```

Lancer le scénario :

```bash
sumo -c scenario.sumocfg
```

## Exécuter la démo Python TraCI

Depuis la racine `src/` :

```bash
python -m v2x_sim.main --scenario scenarios/minimal_v2x/scenario.sumocfg --steps 50
```

Avec interface graphique :

```bash
python -m v2x_sim.main --scenario scenarios/minimal_v2x/scenario.sumocfg --steps 50 --gui
```

## Boucle complète (sans MAB)

Stratégies disponibles :

- `always_direct`
- `always_infrastructure`
- `threshold`

Exemple sur le scénario riche :

```bash
python -m v2x_sim.main \
  --scenario scenarios/rich_v2x/scenario.sumocfg \
  --steps 200 \
  --strategy threshold \
  --danger-distance-m 8 \
  --reward-deadline-ms 120
```

Résumé final affiché :

- nombre d'alertes,
- succès,
- échecs,
- latence moyenne,
- reward cumulée.

## Tests

Lancer toute la suite :

```bash
pytest -q
```

La suite couvre notamment :

- `sumo_runner` avec TraCI mocké,
- `context_builder` (construction + déterminisme),
- `danger_detector` (distance, seuil, stabilité numérique),
- `communication_model` (direct vs RSU, latence, échecs RSU indisponible).
- `reward` (succès rapide, succès tardif, échec de transmission).
