# ECHO-PROJECT
Enregistrement vidéos automatisé pour analyser le comportement de poissons dans des bassins d'observation

![image](https://github.com/user-attachments/assets/cc413941-bcca-44d6-9a1d-5fb1c5894a25)

# Contexte du projet
Le projet de recherche ECHO, financé par l’AAP Observatoire de l’éolien en mer - l’Office
Français de la Biodiversité, se concentre sur les pressions acoustiques liées à l’éolien en mer
sur les mammifères marins et l’ichtyofaune. Ce projet mobilise les compétences
interdisciplinaires de plusieurs partenaires scientifiques et techniques : le laboratoire LIENSs
CNRS – La Rochelle Université, l’ADERA – Cohabys, la Fondation OPEN-C, le Laboratoire LOG
de l’Université du Littoral Côte d’Opale et la société NEREIS Environnement. Lancé en janvier
2024, ce projet de recherche s’étendra sur une durée de trois ans, avec pour objectif
d’approfondir les connaissances sur les interactions entre le développement des énergies
marines renouvelables et la biodiversité marine.
Dans le cadre de ce projet de recherche, une thèse réalisée par Morgane Millot, sous la
direction de Christel Lefrançois et avec le soutien scientifique et technique d’Emmanuel
Dubillot et de Benjamin Bellier, vise à étudier spécifiquement les « pressions acoustiques
liées à l’éolien en mer sur le bar européen (Dicentrarchus labrax) et la sole commune (Solea
solea) dans un contexte de changement climatique ». Pour ce faire, une série
d’expérimentations (en laboratoire, en mésocosme et in situ) a été programmée dans le but
de comprendre les réponses comportementales des poissons engendrées par des
expositions au bruit éolien.
Pour les expérimentations en laboratoire, un groupe de « poissons témoins » (avec bruit non
éolien émis à l’aide d’un haut-parleur) et un groupe de « poissons exposés » (avec bruit éolien
émis à l’aide d’un haut-parleur) seront placés dans deux bassins distincts et acoustiquement
isolés, chacune d’un diamètre de 3.6m et d’une hauteur de 1.2m. Pour chaque bassin, les
groupes de poissons seront divisés en trois arènes d’un diamètre de 0.8m et d’une hauteur
de 0.8m, contenant chacune 3 à 5 poissons. Ainsi, pour étudier les différences de réponses
comportementales initiales (e.g. changements soudains de la vitesse et de la direction de la
nage) ou soutenues (e.g. cohésion du banc) entre conditions, des analyses vidéo sont
nécessaires et la mise en place de caméras est essentielle. Dans un objectif
d’automatisation, de praticité et de réplicabilité, le LIENSs souhaite développer un système
permettant de piloter plusieurs caméras et d’en sortir des données brutes. Ces données
brutes auront pour devenir : 1/ la bancarisation sur support dédié (e.g. NAS, voir ci-dessous)
et sur plateforme de dépôt dans le cadre de la démarche de partage de données et 2/ d’être
traitées et analysées pour calculer plusieurs variables comportementales.

# CAHIER DES CHARGES
### Objet de la demande
Le prestataire a pour objectif principal d’accompagner sur la conception et la mise en place
d’un système connecté « caméras - base de données » en :
Développant un système de visualisation vidéo afin de pouvoir interroger le retour
vidéo en temps réel de chaque caméra individuellement ou collectivement.
Développant un système de pilotage des caméras afin de pouvoir programmer à partir
d’une interface commune le lancement, la fréquence et la durée d’enregistrement
vidéo.
Définissant la procédure pour le stockage de la donnée vidéo brute dans une base de
données dédiée.

### Livrables attendus
Le cahier des charges ci-présent implique la fourniture :
D’un système opérationnel « caméras - base de données »
D’un mode d’emploi intuitif permettant de visualiser le retour vidéo en temps réel
D’un mode d’emploi intuitif permettant de lancer l’enregistrement des caméras en
s’assurant de stocker les données vidéo brutes
D’un format de stockage permettant la réalisation d’une base de données structurée
par rapport aux besoins expérimentaux

# Matériels nécessaires
Caméras → 6 caméras (3 caméras par bassin, et donc 1 caméra par arène)
- Caméra « Basler » modèle « ace Classic acA1300-60gc (CS-Mount) » (https://www.baslerweb.com/fr-fr/shop/aca1300-60gc-cs-mount/)
- Résolution : 1.3 MP & images par seconde : 60
- Caméra conseillée par Tatiana Colchen (éthologue sur espèces aquatiques)
- Conditions pertinentes pour notre étude :
- Compatibilité POE (pour centraliser les caméras utilisées)
- Pas de grand angle (pour éviter les déformations)
- Bonne résolution / qualité de l’image (pour pouvoir bien traiter l’image)
- Possibilité de changer d’objectifs (pour optimiser le champ selon la distance
entre la caméra et l’arène)
- Objectifs → 6 objectifs de 12.5mm (ou autre taille) pour les 6 caméras [modèle « Kowa » de 12.5mm](https://www.baslerweb.com/fr-fr/shop/kowa-lens-lm12hc-f1-4-f12-5mm-1/) : 349€ l’unité
- Hub POE → minimum 6 ports pour les 6 caméras (?€)
- Stockage NAS (fichiers vidéo volumineux et accès à distance)
- Box internet → fournie
- Moniteurs (ordinateur, téléphone) → fournis
- Alimentation → fournie

![image](https://github.com/user-attachments/assets/aecfbcee-0637-4fb5-a61f-2e14f1ba8f26)

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

