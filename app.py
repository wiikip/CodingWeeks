#importation des modules nécessaires pour le fonctionnement
from flask import Flask, render_template, redirect, url_for, session, request, flash, send_from_directory, abort, Response, make_response
import time
from random import choice,randint
from creation_fichier_audio import create_audio_file
import os
from werkzeug.utils import secure_filename
from noteDetection import *
from flask_mysqldb import MySQL
#configuration pour utiliser la base de données sur mysql
from plotHistogram import plotHist

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1' #or 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user_score'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config["CACHE_TYPE"] = "null"
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'static/temp'
NOTES = ["DO","RE","MI","FA","SOL","LA","SI"] # Listes des différentes notes
NB_CHOIX = 4 # Nombre de differents choix
ALLOWED_EXTENSIONS = ["wav"]
TOP_SCORE = 5
antiCache = 0

mysql = MySQL(app)

#préparation des jeux : initialisation
LNoteToPlay = [] #Contient les bonnes note sur la page Jeu 1
LNoteToPlay1 = [] #Contient les bonnes note sur la page Jeu 2
Stack =[] #contient les propositions du joueur 

proposition2 = []
currentLevel = 1

#sysème de login, signin, logout, implémentation du score

@app.route("/disconnection")
def disconnection():
    if 'username' in request.cookies:
        res= redirect('/')
        res.set_cookie("username","username",max_age=0)
        flash("Succesfully Loged-out",'success')
        return res
    else:
        flash("You were not Loged-in","info")
        return redirect('/')
@app.route("/score_game_1", methods=['POST'])
def score_game_1():
    if request.method =='POST':
        if 'username' in request.cookies:
            username = request.cookies.get('username')
            score = 0
            level = int(request.form['level']) 
            score = int(level*(level-1)/2)
            cur = mysql.connection.cursor()
            cur.execute(f"INSERT INTO Scores(Username,Score,Jeux,Niveau) VALUES('{username}',{score},'Game 1',{level})")
            mysql.connection.commit()
            cur.close()
            flash(f"Your score was {score} \n Your Reached level was {level}",'success')
            return redirect('/')
        else:
            flash('Error with your cookies, Are you really loged-in ?','danger')
            return redirect('/')
@app.route("/score_game_2")
def score_game_2():
    
    if 'username' in request.cookies:
        username = request.cookies.get('username')
        score = 0
        level = currentLevel
        score = int((level - 1)*level/2)
        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO Scores(Username,Score,Jeux,Niveau) VALUES('{username}',{score},'Game 2',{level})")
        mysql.connection.commit()
        cur.close()
        flash(f"Your score was {score} \n Your Reached level was {level}",'success')
        return redirect('/')
    else:
        flash('Error with your cookies, Are you really loged-in ?','danger')
        return redirect('/')
@app.route("/Login", methods = ['GET','POST'])  # changer le route
def login(): 
    if request.method =='POST': 
        username = request.form['username']  # changer email -> username
        password = request.form['psw']
        if 'remember' in request.form:
            age = 60*60*24*365
        else:
            age = 60*60
        cur = mysql.connection.cursor()
        result = cur.execute(f"SELECT * FROM Players WHERE Username = '{username}' AND Password='{password}'")
        if result > 0 :
            res= redirect('/')
            res.set_cookie("username",username,max_age=age)
            flash("Succesfully Loged-in",'success')
            return res
        else:
            error = 'Either the Username or Password is not good'
            flash(error,'danger')
            return redirect('/')
    else:
        return redirect('/')

@app.route("/Signin", methods = ['GET','POST'])  # changer le route
def Sign(): 
    if request.method =='POST': 
        username = request.form['username']  
        password1 = request.form['psw']
        password2 = request.form['psw-repeat']
        if 'remember' in request.form :
            age = 60*60*24*365
        else:
            age = 60*60
        cur = mysql.connection.cursor()
        result = cur.execute(f"SELECT * FROM Players WHERE Username = '{username}'")
        if result == 0 :
            if password1 == password2 :
                cur.execute(f"INSERT INTO Players(Username,Password) values('{username}','{password1}')") #mettre le nom de la table 
                mysql.connection.commit()
                flash("Succesfully Signed-in",'success')
                res= redirect('/')
                res.set_cookie("username",username,max_age=age)
                return res
            else:
                error = 'The two passwords are not the same'
                return render_template('home.html',error=error)
        else:                                                                   
            error = 'This username is already taken'
            return render_template('home.html',error=error)
    else:
        return redirect('/')
#gérer le meilleur score 
def Best_rnk_score(Username):
    cur = mysql.connection.cursor()
    result1 = cur.execute(f"SELECT * FROM (SELECT *, CAST(@r:=@r+1 AS SIGNED INTEGER) AS rnk FROM Scores, (SELECT @r:=0 ) AS r WHERE Jeux ='Game 1' ORDER BY Score DESC) AS first WHERE Username = '{Username}' ORDER BY Score LIMIT 1")
    Scores1 = cur.fetchall()
    result2 = cur.execute(f"SELECT * FROM (SELECT *, CAST(@r:=@r+1 AS SIGNED INTEGER) AS rnk FROM Scores, (SELECT @r:=0 ) AS r WHERE Jeux ='Game 2' ORDER BY Score DESC) AS first WHERE Username = '{Username}' ORDER BY Score LIMIT 1")
    Scores2 = cur.fetchall()
    if result1 > 0 :
        Bestrnk1 = Scores1[0]['rnk']
        Bestscore1 = Scores1[0]['Score']
    else:
        Bestrnk1 = None
        Bestscore1 = None
    if result2 > 0 :
        Bestrnk2 = Scores2[0]['rnk']
        Bestscore2 = Scores2[0]['Score']
    else:
        Bestrnk1 = None
        Bestscore1 = None
    return(Bestrnk1,Bestscore1,Bestrnk2,Bestscore2)





def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS








# Pour le jeu 2, variables globales


## ------ HTML Part ------
#page de score générale : affiche les 5 premiers
@app.route('/scores')
def Scores():
    if 'username' in request.cookies:
        username = request.cookies.get('username')
        Loged_in=True
    else:
        Loged_in=False
    # Create cursor
    cur = mysql.connection.cursor()
    # Get Scores
    result1 = cur.execute("SELECT * FROM Scores WHERE Jeux='game 1' ORDER BY Score desc LIMIT " + str(TOP_SCORE))
    Scores1 = cur.fetchall()
    # Close connection
    cur.close()
    #Repeat the same
    cur = mysql.connection.cursor()
    result2 = cur.execute("SELECT * FROM Scores WHERE Jeux='game 2' ORDER BY Score desc LIMIT " + str(TOP_SCORE))
    Scores2 = cur.fetchall()    
    cur.close()
    if result1 > 0 or result2 > 0:
        return render_template('scores.html', Scores1=Scores1, Scores2=Scores2,len1=len(Scores1),len2=len(Scores2),Loged_in=Loged_in)
    else:
        error = 'No Score Found'
        return render_template('home.html', error=error)

#système de follow et unfollow, gestion d'abonnements
@app.route('/follow/<string:follower>/<string:followed>', methods=['POST'])
def follow(follower,followed):
    cur = mysql.connection.cursor()
    result = cur.execute (f"SELECT * FROM Follow WHERE Follower = '{follower}' AND Followed = '{followed}'")
    if result == 0 :
        #ajouter le lien du follow à la base de donnée
        cur.execute(f"INSERT INTO Follow(Follower,Followed) Values('{follower}','{followed}')")
        #commit in the database
        mysql.connection.commit()
        cur.close()
        flash(f"Now you follow {followed}",'info')
        return redirect(f'/scores/{followed}')
    else:
        cur.close()
        flash(f"You already follow {followed}",'danger')
        return redirect(f'/scores/{followed}')
@app.route('/unfollow/<string:follower>/<string:followed>', methods=['POST'])
def unfollow(follower,followed):
    cur = mysql.connection.cursor()
    result = cur.execute (f"SELECT * FROM Follow WHERE Follower = '{follower}' AND Followed = '{followed}'")
    if result == 0 :
        cur.close()
        flash(f"You don't follow {followed}",'danger')
        return redirect(f'/scores/{followed}')
    else :
        cur.execute(f"DELETE FROM Follow WHERE Follower = '{follower}' AND Followed = '{followed}'")
        mysql.connection.commit()
        cur.close()
        flash(f"Now you unfollow {followed}",'warning')
        return redirect(f'/scores/{followed}')
@app.route('/subscriptions')
def Subscriptions():
    if 'username' in request.cookies:
        username = request.cookies.get('username')
        # Create cursor
        cur = mysql.connection.cursor()
        # Get Scores
        result = cur.execute(f"SELECT Followed FROM Follow WHERE Follower = '{username}'")
        Subscriptions = cur.fetchall()
        Best_of_sub=[]
        for sub in Subscriptions :
            dic={ 'Username' : sub['Followed']}
            dic['Bestrnk1'],dic['Bestscore1'],dic['Bestrnk2'],dic['Bestscore2'] = Best_rnk_score(sub['Followed'])
            Best_of_sub.append(dic)
        result1 = cur.execute(f"SELECT * FROM Scores AS S JOIN Follow AS F ON S.Username=F.Followed WHERE Jeux='game 1' AND F.Follower='{username}' ORDER BY Score desc")
        Scores1 = cur.fetchall()
        # Close connection
        cur.close()
        #Repeat the same
        cur = mysql.connection.cursor()
        result2 = cur.execute(f"SELECT * FROM Scores AS S JOIN Follow AS F ON S.Username=F.Followed WHERE Jeux='game 2' AND F.Follower='{username}' ORDER BY Score desc")
        Scores2 = cur.fetchall()    
        cur.close()
        if result1 > 0 or result2 > 0:
            return render_template('Subscriptions.html', Scores1=Scores1, Scores2=Scores2,len1=len(Scores1),len2=len(Scores2),Best_of_sub=Best_of_sub,username=username)
        else:
            error = 'Your subscriptions doesn\'t have any scores'
            return render_template('home.html', error=error)
    else:
        flash("You can't see your subscriptions if you are diconnected, please Log-in",'danger')
        return redirect('/')

#tous les scores pour chaque jeu 
@app.route('/advanced_scores/<string:Game>', methods=['GET','POST'])
def Ad_scores(Game):

    #voir si on a pas eu un submit pour les choix sur les stats
    if request.method == 'POST' :
        NUM_SCORE = request.form['NUMBER']
        ORDER = request.form['ORDER']
    else:
        NUM_SCORE = 5
        ORDER = 'Score'
    cur = mysql.connection.cursor()
    #executer la requet, CAST sert à changer le type des variables de la colonne
    result = cur.execute(f"SELECT *, CAST(@r:=@r+1 AS SIGNED INTEGER) AS rnk FROM Scores, (SELECT @r:=0 ) AS r WHERE Jeux = '{Game}' ORDER BY {ORDER} DESC LIMIT "+str(NUM_SCORE))
    Scores = cur.fetchall()
    
    plotHist([Scores[i]['Score']  for i in range(len(Scores))],Game)
    cur.close()
    if result == 0:
        error='404 error'
        return render_template('home.html', error=error)
    else:
        return render_template('advanced_scores.html', Scores=Scores, len=len(Scores),max=max([Scores[i]['Score'] for i in range(len(Scores))]))

#chercher un joueur dans la base de données, donne son score
@app.route('/search_player', methods=['GET','POST'])
def search():
    if request.method == 'POST' :
        Username = request.form['Username']
        cur = mysql.connection.cursor()
        result = cur.execute(f"SELECT * FROM Players WHERE Username = '{Username}'")
        if result == 0:
            error = 'This user does not exist'
            flash(error,'danger')
            return redirect('/scores')
        else:
            return redirect(f'/scores/{Username}')

@app.route('/scores/<string:Username>', methods=['GET','POST'])
def Score(Username):
    if 'username' in request.cookies:
        username = request.cookies.get('username')
        if request.method == 'POST' :
            NUM_SCORE = request.form['NUMBER']
            ORDER = request.form['ORDER']
        else:
            NUM_SCORE = 5
            ORDER = 'Score'
        cur = mysql.connection.cursor()
        # Get scores in Game 1
        # le fait d'avoir 2 requêtes ici est utile, car la première permet d'avoir le classement, puis la deuxième sert à filtrer (on ne filtre pas avant d'avoir le classement 'Rnk')
        result1 = cur.execute(f"SELECT * FROM (SELECT *, CAST(@r:=@r+1 AS SIGNED INTEGER) AS rnk FROM Scores, (SELECT @r:=0 ) AS r WHERE Jeux ='Game 1' ORDER BY Score DESC) AS first WHERE Username = '{Username}' ORDER BY {ORDER} LIMIT "+str(NUM_SCORE))
        Scores1 = cur.fetchall()
        # Get Scores in Game 2
        result2 = cur.execute(f"SELECT * FROM (SELECT *, CAST(@r:=@r+1 AS SIGNED INTEGER) AS rnk FROM Scores, (SELECT @r:=0) AS r WHERE Jeux ='Game 2' ORDER BY Score DESC) AS first WHERE Username = '{Username}' ORDER BY {ORDER} LIMIT "+str(NUM_SCORE))
        Scores2 = cur.fetchall()
        #obtenir l'avg du score
        avg1=0
        avg2=0
        #----See if we are following this player----
        result = cur.execute(f"SELECT * FROM Follow WHERE Follower = '{username}' AND Followed = '{Username}'")
        if result == 0:
            Isfollowing = False
        else:
            Isfollowing = True
        if result1 > 0:
            for Score in Scores1:
                avg1+=Score['Score']
            avg1=avg1/result1
            bestrnk1 = min([Scores1[i]['rnk'] for i in range(len(Scores1))])
        else:
            bestrnk1 = 0
        if result2 > 0:
            for Score in Scores2:
                avg2+=Score['Score']
            avg2/=result2
            bestrnk2 = min([Scores1[i]['rnk'] for i in range(len(Scores1))])  
        else:
            bestrnk2 = 0          

        if result1 == 0 and result2 == 0:
            error='The User that you want does not exist or doesn\'t have any score'
            return render_template('home.html', error=error)
        else:
        
            return render_template('score.html',Scores1=Scores1,Scores2=Scores2,avg1=avg1,avg2=avg2,bestrnk1=bestrnk1, bestrnk2=bestrnk2,username=username, Isfollowing=Isfollowing )
    else:
        flash('You can\'t access our individual scores if you are not Loged-in','danger')
        return redirect('/')


#système de cookies
@app.route('/')
def home():
    if 'username' in request.cookies:
        username = request.cookies.get('username')
        Texte=f"Hello {username}, You're welcome in this website"
        return render_template('home.html',Texte=Texte, Loged_in=True, username=username)

    else:
        Texte='Log-in Please to have access to our Games'
        Loged_in=False
        return render_template('home.html',Texte=Texte, Loged_in=False)
    
#fonctionnement du jeu 2

@app.route('/2/level/<int:lvl>', methods = ['POST','GET'])
def audioRecorder(lvl):
    global LNoteToPlay1
    global proposition2
    global currentLevel
    if 'username' in request.cookies: #On verifie si l utilisateur est bien connecté
        username = request.cookies.get('username')
        currentLevel = lvl            #On recupere le niveau actuel
        if request.method == 'GET':
            LNoteToPlay1 = []
            for i in range(lvl):#Generation de la liste de notes aléatoires à jouer
                
                NoteToPlay = choice(NOTES) # On choisit aléatoirement une note à jouer
                LNoteToPlay1.append(NoteToPlay)
                
            
        
        if request.method == 'POST': # On récupere un fichier wav uploadé par l'utilisateur  
            
            
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                #
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                flash('Uploaded')
                Tnotes = getListNotes(filename)
                # On enleve les chiffres et les diezes et on met en majuscules
                notes = []
                for n in Tnotes:
                    i = n
                    for j in range(10):
                        i = i.replace(str(j),'')
                    i = i.replace('#','')
                    notes.append(i.upper())
                print(notes)
                proposition2 = notes
                

            return render_template("confirmation.html", nbNotes = len(notes), notes = notes, lvl = lvl ,username=username)

        return render_template('audioRecorder.html', notesToPlay = LNoteToPlay1,username=username)
    else:
        flash('Please Log-in before playing','danger')
        return redirect('/')

@app.route('/confirmation')
def confirmation():#Page de confirmation envoie de la note joué à l'instrument
    return render_template('confirmation.html')

@app.route('/verify')#verification pour savoir si la note jouée est correcte
def verify():
    global currentLevel
    gagne = proposition2 == LNoteToPlay1
    if gagne:
        currentLevel += 1
    else:
        currentLevel = 1 # reset la variable
    return render_template('verify.html', gagne = gagne, lvl = currentLevel)

#page about
@app.route('/about')
def about():
    if 'username' in request.cookies:
        Loged_in = True
    else:
        Loged_in = False
    return render_template('about.html',Loged_in=Loged_in)


## ------------------ Game #1 ------------------ fonctionnement du jeu 1
@app.route('/level/<int:lvl>', methods = ['POST', 'GET'])#JEU 1
def new_game(lvl):
    
    global antiCache
    global LNoteToPlay
    global Stack
    
    if 'username' in request.cookies:
        username = request.cookies.get('username')
        if request.method == 'GET':
            antiCache +=1
        
            Stack = []
        
            print(lvl)
            LNoteToPlay = []
            for i in range(lvl):#Choix des notes à jouer aléatoirement
            
                NoteToPlay = choice(NOTES) # On choisit aléatoirement une note à jouer
                LNoteToPlay.append(NoteToPlay)
    
   
            
                        
                            
                
            disabled = True
            
                

            
            create_audio_file(LNoteToPlay,lvl,antiCache)#Creation fichier audio à jouer
            gagne = None
            
            
        if request.method =='POST':
            if 'choixnote' in request.form:
                
                
                

                Stack.append(request.form['choixnote'])#On ajoute la note proposée à la liste des propositions
                gagne = None

            
            if 'try' in request.form:
                if request.form['try']:
                    gagne = LNoteToPlay == Stack
            if 'del' in request.form:#Supprimer la derniere note des propositions
                if len(Stack) >0:
                    Stack.pop()
                gagne = None
            if len(Stack) < lvl:#On desactive le bouton quand il n'y a pas le bon nombre de notes
                disabled = True
            else:
                disabled = False

        
        print("disabled =",disabled)
        return render_template('jeu_main.html' ,noteToPlay = LNoteToPlay , choixNotes = NOTES, gagne = gagne, proposition = Stack, level = lvl, slevel =str(lvl), disabledButton = disabled,username=username, anticache = str(antiCache))
    else:
        flash('You need to Log-in before playing','danger')
        return redirect('/')
                
    
    
    return render_template('jeu_main.html' ,noteToPlay = LNoteToPlay , choixNotes = NOTES, gagne = gagne, proposition = Stack, level = lvl, slevel =str(lvl), disabledButton = disabled, anticache = str(antiCache))


            






# ----------------------------- Launch server -----------------------------
if __name__ == "__main__":
    app.run(debug=True)

