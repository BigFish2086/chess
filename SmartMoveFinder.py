import random

# assign the king any value which means you can't really lose
# your king as it would be a checkmate before that happened
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0


"""
this is created first to just test the AI moving the pieces
so it wouldn't really so much important to get those moves correct yet
"""


def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


"""
this is should be the method we use to find the
AI best move using a greed-material appraoch
the goals of our AI is to make the socring is as
positive as possible if it playes white and as negative
as possible if it playes black
"""


def findBestMove(gs, validMoves):
    # to alternate between the white and black
    bestPlayerMove = None
    opponentMinMaxScore = CHECKMATE
    turnMultiplier = 1 if gs.whiteToMove else -1
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove


"""
Score the board based on the material
"""


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score

