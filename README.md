#                       Projet audio - Semaine 2 : Création de jeux pédagogiques pour l'apprentissage en musique 

Notre but pendant cette semaine a été de créer des jeux simples autour de la musique pour que des élèves apprenant le solfège ou/et des instruments puissent développer leur oreille en s'amusant. Nous avons donc créé un site HTML comportant 2 jeux différents et un système de scores stockés dans une base de données, ainsi qu'un système de cookies. 
Nous avons entre autre utilisé Flask afin de pouvoir coder en HTML sur Visual Studio Code, et Mysql pour créer la base de données. Pour créer notre site, nous avons dû mettre en relation différentes parties du code que nous avons décrites ci-dessous.

![alt text](collageAudioProject.png "Aperçu du projet")

# La mise en page du site 
Avant tout, pour que le code soit fonctionnel, il est nécessaire d’installer les packages suivants :
Flask, Flask_mysqldb, scipy, matplotlib, numpy, pydub (listés dans requirements.txt)
A installer avec la commande : `pip install -r requirements.txt`
On travaille aussi dans un environnement virtuel qu’il est nécessaire d’activer à chaque démarrage de VS Code, comme expliqué durant la semaine 1.

Nous avons donc utilisé Flask pour pouvoir à la fois écrire en langage HTML sur Visual Studio Code mais aussi coder en Python les différentes rubriques du site. Ainsi, notre fichier principal est app.py, programme python qui appelle des fichiers écrits en HTML. Il suffit d’exécuter le fichier : `python app.py` pour que le site et les jeux soient disponibles. 
Avec le fichier `layout.html`, on designe la partie invariante du site, c’est-à-dire le bandeau qui comporte les différentes rubriques.
Puis pour chaque page, on appelle un fichier html différent dans `app.py`. Par exemple pour la page home : 
```
@app.route(‘/’)
def home() :
return render_template(‘home.html’)
```

Pour mettre en page, nous avons fait appel entre autres à des fichiers css et notamment des flexbox pour le bandeau principal et les touches de piano sur le jeu 1.

# Le fonctionnement du jeu 1 

Lorsque l'on accède à la page (GET), on génère aléatoirement un nombre de notes à jouer dépendant du niveau actuel, et on crée un fichier wav a partir de ces notes qui correspond à la concaténation des sons des différentes notes.
L'utilisateur peut éditer sa proposition de notes et valider si il y a le bon nombre de notes.
Lorsque l'utilisateur valide, on récupère son choix (POST) et on compare sa proposition aux notes réellement jouées, et si les notes coincident, le joueur peut passer au niveau suivant.


# Le fonctionnement du jeu 2

Le principe du jeu 2 est le suivant : le joueur se voit proposer une séquence de notes (sur 1 octave) et doit jouer les notes correspondantes sur son instrument. L’intérêt du jeu est que, pour des instruments tels que la guitare et le violon, un certain apprentissage de la position des notes sur le manche est nécessaire.

Pour améliorer l’expérience utilisateur, le site web est doté d’un enregistreur audio dont le code est dans et dans les fichiers JavaScript dans le dossier *static/scripts*. La page affichée présente un tutoriel qui s’affiche par simple clic sur le "?". En outre, l’utilisateur peut enregistrer autant de fichiers que voulu et les réécouter. S’il est satisfait, il n’a qu’à télécharger le fichier et à l’uploader.

Par la suite, *noteDetection.py* traite le fichier audio et réalise les opérations suivantes :
1. Lire le fichier audio.
2. Récupérer les informations utiles sur le fichier (durée, nombre d'échantillons, fréquence...)
3. Obtenir l'enveloppe du signal.
4. Récupérer les dates de début et de fin pour chaque note (en utilisant l'enveloppe pour s'affranchir des oscillations rapides).
5. Séparer les fichiers dans un dossier *temp*.
6. Réaliser une *transformée de Fourier* pour chacun de ces fichiers et détecter la fréquence du fondamentale.
7. Grâce à la fonction *pitch* implémentée dans le module *noteDetection.py*, on récupère le nom des notes jouées.
8. On renvoie enfin la liste des notes jouées.

Juste après cela, l’utilisateur est renvoyé à la page de confirmation *confirmation.py* où on lui affiche les notes reconnues ainsi que les graphes issus du traitement audio précédent.

S’il l’utilisateur est satisfait, il peut alors valider sa réponse sur *verify.html* et est renvoyé selon sa réponse au niveau suivant ou bien à un écran de défaite (qui ajoute automatiquement son score à la base de données).




# Le fonctionnement de la base de données et des cookies
La connexion ou l'inscription de l'utilisateur crée un cookie dans sont navigateur qui stocke son nom, la checkbox de 'remember me' permet d'augmenter le vie du cookie, ainsi l'utilisateur restera toujours connecté même apprés de longes periodes d'absences. La deconnexion du joueur permet de tuer le cookie, et le retourne à la page d'acceuil.
Lors des sessions de jeux ou lors des pages de score ( hors Top scores ), le cookie qui indique l'utilisateur est indispensable, donc ces pages ne serront pas accessibles sans connexion, si l'utilisateur click sur un ongle qui nécessite d'être conneté, il est redirigé vers la page d'acceuil avec un message qui lui indique qu'il doit se connecter.


