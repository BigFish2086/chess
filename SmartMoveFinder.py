import random

# assign the king any value which means you can't really lose
# your king as it would be a checkmate before that happened
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}

# this is just a way to give some squares some prefrence than other when moving the each piece
knightScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

bishopScores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4],
]

queenScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1],
]

rockScores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4],
]

whitePawnScores = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

blackPawnScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
]

# map eaching of the pieces to the appropriate 2d array
piecePositionScores = {
    "N": knightScores,
    "B": bishopScores,
    "Q": queenScores,
    "R": rockScores,
    "bp": blackPawnScores,
    "wp": whitePawnScores,
}

CHECKMATE = 1000
STALEMATE = 0
# represents how many moves the computer should look ahead
# before deciding on its best move
MAX_DEPTH = 3
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


def findBestMoveMinMax(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    findMoveNegaMaxAlphaBeta(
        gs, validMoves, MAX_DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1
    )
    returnQueue.put(nextMove)
    print(returnQueue.get())


"""
implementing the nega-max algorithm
"""


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    # move ordering - could improve the algorithm a little bit
    # random.shuffle(validMoves)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(
            gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier
        )
        if score > maxScore:
            maxScore = score
            if depth == MAX_DEPTH:
                nextMove = move
                print(move, score)
        gs.undoMove()
        if maxScore > alpha:  # where the prunning happens
            alpha = maxScore
        if alpha >= beta:
            break
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
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                pps = 0
                fac = 0.1
                color = square[0]
                piece = square[1]
                if piece != "K":
                    pps += (
                        piecePositionScores[piece if piece != "p" else square][row][col]
                        * fac
                    )
                if color == "w":
                    score += pieceScore[piece] + pps
                elif color == "b":
                    score -= pieceScore[piece] + pps
    return score
