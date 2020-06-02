# pylayers

Layer based visualization framework for experimental geodata and search algorithms visualisation.

> install dependencies with `sudo apt install python-qt4-dev pyqt4-dev-tools` command


### content

- [OSM layer](#OSM-layer)
- [bidirectional dijkstra layer](#bidirectional-dijkstra-layer)
- [dijkstra layer](#dijkstra-layer)
- [location layer](#location-layer)
- [custom layer](#custom-layer)


## OSM layer

OSM (Open Street Map) layer integration into pylayers framework (serves as a base for other layers).

Run with 

```bash
cd osm_layer
python pylayers.py
```

commands.

![osm_layer screenshot](docs/osm_layer.jpg)


## bidirectional dijkstra layer

Bidirectional dijkstra based route calculation layer.

Run with

```bash
cd bidi_dijkstra
python pylayers.py
```

commands a open `test/data/romanova.bgrp` bidirectional graph file by pressing `o` key.

![bidi_dijkstra layer with small graph loaded screenshot](docs/bidi_dijkstra.jpg)

> What about graph generator? Make a note about it.


## dijkstra layer

Dijkstra based route calculation layer.

Run with

```bash
cd dijkstra
python pylayers.py
```

commands.


## location layer

Layer to visualize line based gps log file.

> describe log file structure (as I remember it was gump from android device, maybe we still have the app)


## custom layer

> a few lines how to implement new layer 

