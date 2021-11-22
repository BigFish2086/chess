import random

# assign the king any value which means you can't really lose
# your king as it would be a checkmate before that happened
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
# represents how many moves the computer should look ahead
# before deciding on its best move
MAX_DEPTH = 2
nextMove = None


"""
this is created first to just test the AI moving the pieces
so it wouldn't really so much important to get those moves correct yet
"""


def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


"""
this is a helper method to make the first calls
for the actual algorithm
"""


def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveNegaMax(gs, validMoves, MAX_DEPTH, 1 if gs.whiteToMove else -1)
    return nextMove


"""
implementing the nega-max algorithm
"""


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == MAX_DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


"""
a little bit more instructive score board method instead of
the naive solution that's implemented in scoreMaterial()
notes:
 1. postive score is good for white and negative score is good for black
"""


def scoreBoard(gs):
    # checking for those two basic cases here instead of doing
    # that in the findMoveMinMax()
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score
