import matplotlib.pyplot as plt

def plotHist(lData, game):
    '''lData is a list of the data you want to plot
    game is a string containing the name of the game
    Save the file in static/graphs/histGame to allow display in the leaderboard webpage.'''
    plt.hist(lData,bins=10,color="lightcoral")
    plt.ylabel('Number of people')
    plt.xlabel('Score')
    plt.title('Histogram of scores for ' +game)


    plt.savefig('static/graphs/histGame.png', dpi=150)
    return