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
        self.pins = []
        self.checks = []
        self.inCheck = []
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # to hold squares where in en-passant capature can happen

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
        # if pawn moves twice, next move can capture en-passant
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enpassantPossible = ()
        # if en-passant move, then we must update the board to capture the pawn
        if move.enPassant:
            self.board[move.startRow][move.endCol] = "--"
        # if pawn promotion, then change the piece
        if move.pawnPromotion:
            # later we should change this to promote to any allowd piece
            # promotedPiece = input("promote to Q, R, B or N") # we can make this part of the ui later
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

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
            # undo en-passant move
            if move.enPassant:
                # remove the pawn that was added in the wrong square
                self.board[move.endRow][move.endCol] = "--"
                # puts the pawn back to the square, it was captured from
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                # allow an en-passant to happen on the next move
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo a 2 square pawn advance and that should reset enpassantPossible again
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

    """
    all moves considering even if the king is in check
    """

    def getValidMoves(self):
        # the more advanced solution
        moves = []
        # 1. check for pins and checks
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # only one check, then block, move or take
                moves = self.getAllPossibleMoves()
                # the block part:
                check = self.checks[0]  # info about the check
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # squares that piece can move to
                if pieceChecking[1] == "N":  # if knight, then capture, move
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        # once get to piece and checks
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                    # get move of any moves that don't block check and move the king
                    # when removing from a list, remove from backword
                    for i in range(len(moves) - 1, -1, -1):
                        # move doesn't move king, so it must block or captue
                        if moves[i].pieceMoved[1] != "K":
                            # move doesn't block check or capture piece
                            if not (moves[i].endRow, moves[i].endCol) in validSquares:
                                moves.remove(moves[i])
            else:  # double check, then king has to move
                self.getKingMove(kingRow, kingCol, moves)
        else:  # no checks, then all the moves are valid minus those for pins
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = True
            self.staleMate = True

        return moves

    def checkForPinsAndChecks(self):
        pins = []  # to hold where the allied pinned piece and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # then let's check outword from the king for pins and checks
        directions = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset the possible pin
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        # {and endPiece[1] != 'K'} this part of the if condition is to
                        # prevent the imaginary king to be protected by the real king on the board
                        if possiblePin == ():  # the 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            # hitting the 2nd which means that there's no pins or checks from this direction
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        # based on the enemy piece type, we have 5 different possiblities
                        # 1. orthogonally away from the king and type is rook
                        # 2. diagonally away from the king and type is bishop
                        # 3. one square away and type is pawn
                        # 4. any direction and type is queen
                        # 5. any square away and piece is a king
                        if (
                            (0 <= j <= 3 and pieceType == "R")
                            or (4 <= j <= 7 and pieceType == "B")
                            or (
                                i == 1
                                and pieceType == "p"
                                and (
                                    (enemyColor == "w" and 6 <= j <= 7)
                                    or (enemyColor == "b" and 4 <= j <= 5)
                                )
                            )
                            or (pieceType == "Q")
                            or (i == 1 and pieceType == "K")
                        ):
                            if (
                                possiblePin == ()
                            ):  # means there's no piece bloking the check from that direction
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # that means there's a blocking piece, so pi it
                                pins.append(possiblePin)
                                break
                        else:  # this case means the enemy piece doesn't applay a check
                            break
                else:  # we become out of the board
                    break
        # for the knight checks
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
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                # means enemy knight attacking king
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        pawnPromotion = False

        if self.board[r + moveAmount][c] == "--":  # 1 square move
            if not piecePinned or pinDirection == (moveAmount, 0):
                if (
                    r + moveAmount == backRow
                ):  # if the pawn gets to the back rank, then it's a promotion
                    pawnPromotion = True
                moves.append(
                    Move(
                        (r, c),
                        (r + moveAmount, c),
                        self.board,
                        pawnPromotion=pawnPromotion,
                    )
                )
                if (
                    r == startRow and self.board[r + 2 * moveAmount][c] == "--"
                ):  # 2 square move
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
        if c - 1 >= 0:  # left capture
            if not piecePinned or pinDirection == (moveAmount, -1):
                if (
                    self.board[r + moveAmount][c - 1][0] == enemyColor
                ):  # we need check if that an enemy first
                    if (
                        r + moveAmount == backRow
                    ):  # if the pawn gets to the back rank, then it's a promotion
                        pawnPromotion = True
                    moves.append(
                        Move(
                            (r, c),
                            (r + moveAmount, c - 1),
                            self.board,
                            pawnPromotion=pawnPromotion,
                        )
                    )
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:  # the king is left to the pawn
                            # inside is between the king and the pawn and the outside is between pawn and the border
                            insideRange = range(kingCol + 1, c - 1)
                            outsideRange = range(c + 1, 8)
                        else:  # the king is to the right of the pawn
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c - 2, -1, -1)
                        for i in insideRange:
                            if (
                                self.board[r][i] != "--"
                            ):  # some other piece beside the enpassant pawn
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (
                                square[1] == "R" or square[1] == "Q"
                            ):  # attacking piece
                                attackingPiece = True
                            elif square[0] != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(
                            Move(
                                (r, c),
                                (r + moveAmount, c - 1),
                                self.board,
                                enPassant=True,
                            )
                        )
        if c + 1 <= 7:  # right capture
            if not piecePinned or pinDirection == (moveAmount, 1):
                if (
                    self.board[r + moveAmount][c + 1][0] == enemyColor
                ):  # we need check if that an enemy first
                    if (
                        r + moveAmount == backRow
                    ):  # if the pawn gets to the back rank, then it's a promotion
                        pawnPromotion = True
                    moves.append(
                        Move(
                            (r, c),
                            (r + moveAmount, c + 1),
                            self.board,
                            pawnPromotion=pawnPromotion,
                        )
                    )
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:  # the king is left to the pawn
                            # inside is between the king and the pawn and the outside is between pawn and the border
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c + 2, 8)
                        else:  # the king is to the right of the pawn
                            insideRange = range(kingCol - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            if (
                                self.board[r][i] != "--"
                            ):  # some other piece beside the enpassant pawn
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (
                                square[1] == "R" or square[1] == "Q"
                            ):  # attacking piece
                                attackingPiece = True
                            elif square[0] != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(
                            Move(
                                (r, c),
                                (r + moveAmount, c + 1),
                                self.board,
                                enPassant=True,
                            )
                        )

    """
    all moves for a knight located at row:r and column:c
    then this move to the list
    """

    def getKnightMove(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                if self.board[r][c][1] != "Q":
                    # can'r remove queen from pin on rook moves, only remove it from bishop moves
                    self.pins.remove(self.pins[i])
                break

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
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    all moves for a bishop located at row:r and column:c
    then this move to the list
    """

    def getBishopMove(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    # can'r remove queen from pin on rook moves, only remove it from bishop moves
                    self.pins.remove(self.pins[i])
                break
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
                    if (
                        not piecePinned
                        or pinDirection == d
                        or pinDirection == (-d[0], -d[1])
                    ):
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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    # can'r remove queen from pin on rook moves, only remove it from bishop moves
                    self.pins.remove(self.pins[i])
                break

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
                    if (
                        not piecePinned
                        or pinDirection == d
                        or pinDirection == (-d[0], -d[1])
                    ):
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
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # empty or enemy piece
                    # place king on empty square and check for checks
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # place king back on the original location
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "0": 0}

    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    fileToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

    colsToFiles = {v: k for k, v in fileToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant=False, pawnPromotion=False):
        self.startRow, self.startCol = startSq
        self.endRow, self.endCol = endSq
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # pawn promotion
        self.pawnPromotion = pawnPromotion

        # en-passant move
        self.enPassant = enPassant
        if enPassant:
            self.pieceCaptured = (
                "bp" if self.pieceMoved == "wp" else "wp"
            )  # captures opposite color pawn

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
