"""
This is responsiwle for storing all the information about the current state
of the chess game. Also, be responsible for determining the valid moves at
the current state. And it'll keep a move log.
"""


class GameState:
    def __init__(self):
        # this is a 2d representation of the board from white prespective
        # to gain some more speed, we might use numpy library instead
        # the representation is pretty easy:
        # the first character is about the piece color: b = black, w = white
        # and the second one is the piece standard notation:
        # K = King, Q = Queen, R = Rook, B = Bishop, N = Knight, p = pawn
        # finally, "--" is for empty squares
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # 8th rank
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # 7th rank
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 6th rank
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 5th rank
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 4th rank
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 3th rank
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # 2th rank
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],  # 1th rank
        ]

        self.whiteToMove = True
        self.moveLog = []  # Move objects
        self.moveFunctions = {
            "p": self.getPawnMove,
            "N": self.getKnightMove,
            "B": self.getBishopMove,
            "R": self.getRockMove,
            "Q": self.getQueenMove,
            "K": self.getKingMove,
        }
        # to keep track of the kings locations becuase:
        # castling, checks, checkmates and stalemates
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        # the corrdinates where an enpassant capture is possible
        self.enpassantPossible = ()

    """
    This functions takes a move as a parameter and executes it
    Note: this won't work now quite well for castling, pawn promotion and en-passant
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # log the move, so we can undo it later or print a PNG for the game
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove  # switch turns
        # update the both of the kings location after making a move
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # about pawn promotions, we'll consider the queen promotion at first:
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # about enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # capturing the pawn
        # update the enpassantPossible variable
        # only for 2 square pawn advance
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

    """
    undo the last move made on the board
    """

    def undoMove(self):
        # first let's make sure that there's a move to undo
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns
            # update the both of the kings location after undo a move
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # delete checkmate and stalemate states
            self.checkMate = False
            self.staleMate = False
            # undo the enpassant move
            if move.isEnpassantMove:
                # we make the landing square blank as it was
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo 2 square pawn advance
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

    """
    all moves considering even if the king is in check
    """

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        # the easy, but not efficient solution is:
        # 1. let's generate all the possible moves and don't worry about the kings state
        moves = self.getAllPossibleMoves()
        # 2. for each move found, make that move
        # when removing from the list, go backwords :)
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # 3. generate all opponent's moves
            # 4. for each of those moves, check if they attack your king
            # we need this as the makeMove() did swap the players once
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 5. if they do, it's not a valid move
                moves.remove(moves[i])
            # we need this to return every thing as before
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        # do we have a checkmate |:) or stalemate (:|
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        return moves

    """
    to determine if the current player is in check
    """

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(
                self.whiteKingLocation[0], self.whiteKingLocation[1]
            )
        else:
            return self.squareUnderAttack(
                self.blackKingLocation[0], self.blackKingLocation[1]
            )

    """
    to determine if the enemy can attack the square(r, c)
    """

    def squareUnderAttack(self, r, c):
        # first switch to the opponents move
        self.whiteToMove = not self.whiteToMove
        # generate all of its moves
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch the turns back
        # check if any of those moves is attacking my kings location
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # now my king is under attack
                # note: we have done the move on our back end, so no need to undoMove() it
                return True
        return False  # none of my opponents move will be attacking my king

    """
    all moves without considering checks
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            # number of columns in a given row
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # the piece color
                if (turn == "w" and self.whiteToMove) or (
                    turn == "b" and not self.whiteToMove
                ):
                    piece = self.board[r][c][1]  # the piece type
                    # generate the all possible valid moves for each piece
                    # a more better version of an if statemnet
                    self.moveFunctions[piece](r, c, moves)
        return moves

    """
    all moves for a pawn located at row:r and column:c
    then this move to the list
    """

    def getPawnMove(self, r, c, moves):
        if self.whiteToMove:  # white pawn move
            if self.board[r - 1][c] == "--":  # the square in front of a pawn is empty
                # startSquare, endSquare, board
                moves.append(Move((r, c), (r - 1, c), self.board))
                # check if it possible to advance to squares in the first move
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # don't go outside the board from the left :)
                if (
                    self.board[r - 1][c - 1][0] == "b"
                ):  # there's an enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True)
                    )
            if c + 1 <= 7:  # don't go outside the board from the right :)
                if (
                    self.board[r - 1][c + 1][0] == "b"
                ):  # there's an enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True)
                    )

        else:  # black pawn move
            if self.board[r + 1][c] == "--":  # the square in front of a pawn is empty
                # startSquare, endSquare, board
                moves.append(Move((r, c), (r + 1, c), self.board))
                # check if it possible to advance to squares in the first move
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # don't go outside the board from the left :)
                if (
                    self.board[r + 1][c - 1][0] == "w"
                ):  # there's an enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True)
                    )
            if c + 1 <= 7:  # don't go outside the board from the right :)
                if (
                    self.board[r + 1][c + 1][0] == "w"
                ):  # there's an enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True)
                    )

        # paw promotions will be added later..

    """
    all moves for a knight located at row:r and column:c
    then this move to the list
    """

    def getKnightMove(self, r, c, moves):
        # the logic here is somehow different than the rock of the bishop
        # as that the knight is a short range piece
        # (row, col) representation for the 8 possible moves
        knightMoves = (
            (-1, -2),
            (-1, 2),
            (-2, -1),
            (-2, 1),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    all moves for a bishop located at row:r and column:c
    then this move to the list
    """

    def getBishopMove(self, r, c, moves):
        # (row, col) representation for the 4 diaganol moves
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if (
                    0 <= endRow < 8 and 0 <= endCol < 8
                ):  # the rock will still be on the board :)
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        # empty square, so we can reach it and check \
                        # if we can reach more squares after that
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        # that's our enemy, so we can still capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        # but if we had to capture, then we can't check for more moves
                        # in that direction
                        break
                    else:
                        # friendly piece in the way, so we can't check that direction anymore
                        break
                else:  # we can't go out of the board
                    break

    """
    all moves for a rock located at row:r and column:c
    then this move to the list
    """

    def getRockMove(self, r, c, moves):
        # (row, col) representation
        # and from the white prespective, the rock can move:
        # up, left, down, right
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if (
                    0 <= endRow < 8 and 0 <= endCol < 8
                ):  # the rock will still be on the board :)
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        # empty square, so we can reach it and check \
                        # if we can reach more squares after that
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        # that's our enemy, so we can still capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        # but if we had to capture, then we can't check for more moves
                        # in that direction
                        break
                    else:
                        # friendly piece in the way, so we can't check that direction anymore
                        break
                else:  # we can't go out of the board
                    break

    """
    all moves for a queen located at row:r and column:c
    then this move to the list
    """

    def getQueenMove(self, r, c, moves):
        # as the queen has the power of both the rook and a bishop
        # it makes that code a lot easier
        self.getBishopMove(r, c, moves)
        self.getRockMove(r, c, moves)

    """
    all moves for a king located at row:r and column:c
    then this move to the list
    """

    def getKingMove(self, r, c, moves):
        kingMoves = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),  # from the rock
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )  # from the bishop
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "0": 0}

    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    fileToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

    colsToFiles = {v: k for k, v in fileToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False):
        self.startRow, self.startCol = startSq
        self.endRow, self.endCol = endSq
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # enpassant move
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"

        # pawn promotion move
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (
            self.pieceMoved == "bp" and self.endRow == 7
        )

        # a unique id for each move in the range of 0 and 7777
        self.moveID = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )
        # print(self.moveID) # for debugging

    """
    overriding the equals method: maybe like copy or move constructors
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # this can be modified to be a more real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
