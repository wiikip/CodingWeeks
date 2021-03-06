CREATE TABLE Scores (id INT(11) AUTO_INCREMENT PRIMARY KEY, Username VARCHAR(25), Score INT(25), Jeux VARCHAR(25), Niveau Int(11), Qlq TEXT, Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (Username) REFERENCES Players(Username));

CREATE TABLE Players (Username VARCHAR(25) PRIMARY KEY, Password VARCHAR(256), Email VARCHAR(256), Sex VARCHAR(10), Adresse Varchar(256), Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE Follow (Follower Varchar(25), Followed Varchar(25), FOREIGN KEY(Follower) REFERENCES Players(Username), FOREIGN KEY(Followed) REFERENCES Players(Username), PRIMARY KEY(Follower,Followed));

INSERT INTO Players(Username) VALUES('Joueur 1');
INSERT INTO Scores(Username,Score,Jeux,Niveau,Qlq) VALUES ('Joueur 1',1428,'Game 2',33,"c'est seulement un teste ce truc Ok");




SELECT id, Username,Score, @r := @r + 1 AS rank
FROM Scores, (SELECT @r := 0) AS r
ORDER BY Score

SELECT *
From (
	SELECT *,@r:=@r+1 AS rnk
	From Scores, (SELECT @r:=0) As r
	)
WHERE Jeux ='Game 1' AND Username= %s
LIMIT		



