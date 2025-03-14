# ECHO-PROJECT
Enregistrement vidéos automatisé pour analyser le comportement de poissons dans des bassins d'observation

# Contexte du projet

Le projet de recherche ECHO, financé par l’AAP Observatoire de l’éolien en mer - l’Office Français de la Biodiversité, se concentre sur les pressions acoustiques liées à l’éolien en mer sur les mammifères marins et l’ichtyofaune. Ce projet mobilise les compétences interdisciplinaires de plusieurs partenaires scientifiques et techniques : le laboratoire LIENSs CNRS – La Rochelle Université, l’ADERA – Cohabys, la Fondation OPEN-C, le Laboratoire LOG de l’Université du Littoral Côte d’Opale et la société NEREIS Environnement. 

Lancé en janvier 2024, ce projet de recherche s’étendra sur une durée de trois ans, avec pour objectif d’approfondir les connaissances sur les interactions entre le développement des énergies marines renouvelables et la biodiversité marine. Dans le cadre de ce projet de recherche, une thèse réalisée par Morgane Millot, sous la direction de Christel Lefrançois et avec le soutien scientifique et technique d’Emmanuel Dubillot et de Benjamin Bellier, vise à étudier spécifiquement les « pressions acoustiques liées à l’éolien en mer sur le bar européen (Dicentrarchus labrax) et la sole commune (Solea
solea) dans un contexte de changement climatique ». 

Pour ce faire, une série d’expérimentations (en laboratoire, en mésocosme et in situ) a été programmée dans le but de comprendre les réponses comportementales des poissons engendrées par des expositions au bruit éolien. Pour les expérimentations en laboratoire, un groupe de « poissons témoins » (avec bruit non éolien émis à l’aide d’un haut-parleur) et un groupe de « poissons exposés » (avec bruit éolien émis à l’aide d’un haut-parleur) seront placés dans deux bassins distincts et acoustiquement isolés, chacune d’un diamètre de 3.6m et d’une hauteur de 1.2m. Pour chaque bassin, les groupes de poissons seront divisés en trois arènes d’un diamètre de 0.8m et d’une hauteur de 0.8m, contenant chacune 3 à 5 poissons. 

Ainsi, pour étudier les différences de réponses comportementales initiales (e.g. changements soudains de la vitesse et de la direction de la nage) ou soutenues (e.g. cohésion du banc) entre conditions, des analyses vidéo sont nécessaires et la mise en place de caméras est essentielle. Dans un objectif d’automatisation, de praticité et de réplicabilité, le LIENSs souhaite développer un système permettant de piloter plusieurs caméras et d’en sortir des données brutes. Ces données brutes auront pour devenir : 
- 1/ la bancarisation sur support dédié (e.g. NAS, voir ci-dessous) et sur plateforme de dépôt dans le cadre de la démarche de partage de données
- 2/ d’être traitées et analysées pour calculer plusieurs variables comportementales.

# Schéma de principe
![Echo_Project_Schema2](https://github.com/user-attachments/assets/be0a8e73-cec2-4a45-88d7-8884c86ef8c7)

# CAHIER DES CHARGES
### Objetif

Développer un système de visualisation vidéo afin de pouvoir interroger le retour vidéo en temps réel de chaque caméra individuellement ou collectivement. Piloter des caméras afin de pouvoir programmer à partir d’une interface commune le lancement, la fréquence et la durée d’enregistrement
vidéo. Stocker de la donnée vidéo brute en provenance de multiple fluxs vidéo

### Livrables attendus
Le cahier des charges ci-présent implique la fourniture :
D’un système opérationnel « caméras - base de données »
D’un mode d’emploi intuitif permettant de visualiser le retour vidéo en temps réel
D’un mode d’emploi intuitif permettant de lancer l’enregistrement des caméras en
s’assurant de stocker les données vidéo brutes
D’un format de stockage permettant la réalisation d’une base de données structurée
par rapport aux besoins expérimentaux

# Matériels nécessaires
### Conditions pertinentes pour notre étude :
Caméras → 6 caméras (3 caméras par bassin, et donc 1 caméra par arène) + POE (pour centraliser les caméras utilisées ET n'avoir qu'un fil pour alimenter & récupérer les fluxs vidéos ) + RTSP pour capter le flux vidéo et paramétrer l'encodage
- [Caméra Zowietek ~ 269€ / unité ](https://www.amazon.fr/zowietek-ZowieCAM-Diffusion-Autonome-lenseignement/dp/B0CWRP5PDR?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=6XOEYNRA11FV&dib=eyJ2IjoiMSJ9.jAZmvlJeKmbN6wKwXEzbkZN597AGFJ1ESrbydCokUDFYY_rEZBlbjQwmPnNpdZrrFhIoXwdVZsCcMv97RdxP64uzGgRHaYBRijTeEZdTRik8wIIa7zJbs5tzIjXj54R8NPVPsM4p6kCQtMt0hWXQGjNPfESFG4_I0365MOHdHbOdFjvunqcaJfDqk5GUptVCgOW-yNCgZjxy1iXO4lRAWqhys3_3dp8z-BRhtUEVY3gryN69hKag7iEWhEpb66KF5zjZ06e6aQ69OU9eSZztQNjU38I4cDOKFRf2LeSIwWg.M4zdJnlismJ0GzaKlJ1bOT3XcNebTDprpLUF3PKiTZg&dib_tag=se&keywords=4K%2BNDI%2BPOV%2BCamera%2C%2BC%2FCS%2BModel&qid=1739274794&sprefix=4k%2Bndi%2Bpov%2Bcamera%2C%2Bc%2Fcs%2Bmodel%2Caps%2C122&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1)
- Pas de grand angle (pour éviter les déformations)
- Bonne résolution / qualité de l’image (pour pouvoir bien traiter l’image)
- Possibilité de changer d’objectifs (pour optimiser le champ selon la distance
entre la caméra et l’arène)
- Switch POE → minimum 6 ports pour les 6 caméras [(~ 200€)](https://www.amazon.fr/Ethernet-position-rackable-Protection-Garantie/dp/B07DFF8GSZ?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3PP0BHI52XC71&dib=eyJ2IjoiMSJ9.SOsrRYn3MQxQXegvFx7JecY--yo8Kr5r7cZwhiNlgzoe67sTqWvmh82iPvrGmXMyK9tJzGppD95gDx3-kXqN2EcZtGWEqZba-YHgsKgVgLdbeZwX_7tLQgvPNvgQ5NYgimmWENbZNsYdiEe9FnqSOLLYaJoEsw5vvPosF84A3qJwzgRBOxcNttZgZPu2G2IkpPJSRmvIvgFiJS5esVXFtKgIjhSzwf7vJjeQk4GrHy5gJ1_kTu1AfAW77eeLfcGiLoRixA5FnL6WM1VwNzMjXgTh_OA5OhPeMLRPGH28uUbriiDoZo1LxbE-yr4WrtgpHe34EZ6n7--9yByPnH1ps0JqRNhPJb9M9FaXUG9ar4c.M7E2fa5sTtnpy5ZLh_utN6NzEn7X0eUj5GZ_pUXxwRg&dib_tag=se&keywords=16%2BPOE%2BSwitch%2Bcisco&qid=1739865976&s=computers&sprefix=16%2Bpoe%2Bswitch%2Bcisco%2Ccomputers%2C100&sr=1-5&th=1)
- [Stockage NAS ~ 547€ ]((https://www.reichelt.com/fr/fr/shop/produit/boitier_vide_pour_serveur_nas_diskstation_ds423_-344247)) (fichiers vidéo volumineux et accès à distance)
- Box internet → fournie
- Moniteurs (ordinateur, téléphone) → fournis
- Alimentation → fournie
- [Raspberry pi 5  ( avec Shield SSD ~ 219€ )](https://www.amazon.fr/dp/B0DSSZ1ZZD?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1) pour l'hébergement des applicatifs ( Node-Red, GStreamer, service python )

# Spécificités annexes pour la base de données
Autres points importants :
- Les scenarii sonores auxquels les animaux seront exposés vont être pré-établis et pré-
enregistrés.
- Chacun des scenarii peut varier en termes de durée totale, de durée de chacun des
événements sonores le constituant, de durée entre évènements sonores consécutifs.
- Normaliser les données en fonction d’un référentiel commun, c’est-à-dire en fonction de l’heure universelle (UTC), e.g. potentiellement utiliser des balises GPS avec ce même référentiel.
- Pouvoir lancer le dispositif, au choix, sur un des deux bassins ou sur les deux bassins.
- Avoir un ID par caméra (autrement dit par arène) et par bassin (qui sera éventuellement équivalent à une condition expérimentale spécifique).
- Bien définir le format de sortie des vidéos, c’est-à-dire que le logiciel de [AnimalTA](http://vchiara.eu/index.php/animalta) lit des fichiers « .avi ».
- Sortie vidéo : chaque dossier « série » contiendra différentes « séquences » vidéos spécifiques à une « série », un « bassin », une « arène », une « date de début », un « horaire (hh:mm:ss) de début », une « date de fin » et un « horaire (hh:mm:ss) de fin », avec le format de nom suivant :
« IDSERIE_IDBASSIN_IDARENE_IDSEQUENCE_DATESTART_HSTART_ DATEEND_HEND.avi ».

## Schéma de principe des positionnemnts des caméras

![image](https://github.com/user-attachments/assets/aecfbcee-0637-4fb5-a61f-2e14f1ba8f26)

## Configuration des caméras 

![encoder_settings_zowietek](https://github.com/user-attachments/assets/12663b70-a90c-4b4f-b008-ce3426d73a9d)

