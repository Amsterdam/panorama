Basisinformatie maakt binnen een opnameseizoen dagelijks opnames.
Elke opnamedag worden er 'missies' aangemaakt.
Binnen een missie komen 1 of meerdere 'runs' voor. Een run is een
aaneengesloten opname van meerdere beelden.

Basisinformatie verwerkt de ruwe opnames en de ruwe navigatiegegevens,
en upload deze naar de bestandsserver van
Datapunt.

De mappenstructuur is `<panoserver>/YYYY/MM/DD/<missienaam>/`.

Bijvoorbeeld: `<panoserver>/2016/04/11/TMX7315120208-000027/`.

In elke map komen de volgende bestanden voor:
1. pano_<run>_<panorama-id>.jpg
2. panorama1.csv
3. trajectory.csv
4. Camera_xxxxxxxx_YYYYMMDD.sync
5. <missienaam>_xxxxxxx.log

Per dag / missie worden de volgende bestanden gegenereerd:
Ad 1)   de beelden zelf. Er is altijd 1 Run binnen een missie.
        De run-nummering begint bij 0. De panorama-id is een
        nulgebaseerd volgnummer binnen de run. Bijvoorbeeld:
        de tweede afbeelding binnen de 3e run heet: `pano_0002_000001.jpg`.
Ad 2)   opnamelocaties en metadata van de beelden
Ad 3)   metadata van het gereden traject,inclusief de kwaliteit van
        de navigatie.
Ad 4)   aanvullende informatie over de opnametijden
Ad 5)   procesinformatie van de missie, waaronder de missienaam

Op dit moment zijn de eerste 3 bestanden relevant.
De structuur van de twee csv-bestanden (2) en (3) wordt hieronder
toegelicht.

### panorama1.csv ###
Tab-gescheiden

Bevat de metadata van de opnames.

| kolomnaam                 | voorbeeld         | betekenis     |
|-------------------------- | ----------------- | --------------|
| `gps_seconds[s]`          | 1119865163.26577  | tijd          |
| `panorama_file_name`      | pano_0000_000000  | bestandsnaam  |
| `latitude[deg]`           | 52.3637434695634  | opnamelocatie |
| `longitude[deg]`          | 5.1860815788512   |               |
| `altitude_ellipsoidal[m]` | 42.3710962571204  |               |
| `roll[deg]`               | -2.04336774663454 | camerastand   |
| `pitch[deg]`              | 1.8571838859381   |               |
| `heading[deg]`            | 359.39712516717   |               |

### trajectory.csv ###
Tab-gescheiden

Bevat de metadata van het gereden traject, inclusief de kwaliteit
van de navigatie.
Deze gegevens zijn niet nodig om de opnamelocaties en de
beelden zelf te tonen, maar kunnen gebruikt worden als een
indicatie van waar gereden is, en als indicatie
van de navigatiekwaliteit.

| kolomnaam                 | voorbeeld          | betekenis     |
|-------------------------- | ------------------ | --------------|
| `gps_seconds[s]`          | 1119864909.00311	 | tijd          |
| `latitude[deg]`           | 52.3638859873144	 | locatie       |
| `longitude[deg]`          | 5.18583889988423	 |               |
| `altitude_ellipsoidal[m]` | 42.1257964957097	 |               |
| `north_rms[m]`            | 0.0337018163617934 | kwaliteit     |
| `east_rms[m]`	            | 0.0254896778492272 |               |
| `down_rms[m]`	            | 0.041721045361001	 |               |
| `roll_rms[deg]`           | 0.0294313546384066 |               |
| `pitch_rms[deg]`          | 0.0310816854803103 |               |
| `heading_rms[deg]`	    | 0.208372506807263	 |               |




