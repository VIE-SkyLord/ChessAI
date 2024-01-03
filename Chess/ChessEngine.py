# File tính các nước đi khả dụng ở trạng thái đang xét, ghi lại lịch sử nước đi

class GameState():
    def __init__(self):
        # Bàn cờ theo góc nhìn bên trắng
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        # Lượt trắng đi
        self.whiteToMove = True
        self.moveLog = []
        # vị trí ban đầu của vua
        self.blackKingLocation = (0, 4)
        self.whiteKingLocation = (7, 4)
        self.checkMate = False
        self.staleMate = False
        self.isEnpassantMove = ()
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.enpassantPossible = ()
        self.inCheckAttribute = False
        self.pins = []
        self.checks = []

    # xử lý sau khi quân thực hiện nước đi
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # ghi lại nước đi
        self.moveLog.append(move)
        # Đổi người chơi
        self.whiteToMove = not self.whiteToMove
        # cập nhật vị trí của vua khi vua di chuyển
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # phong tốt
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capturing the pawn

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # nước đi nhập thành
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # nước đi nhập thành phía bên vua
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # di chuyển quân xe
                self.board[move.endRow][move.endCol + 1] = '--'  # xóa quân xe cũ
            else:  # phía bên hậu
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # di chuyển quân xe
                self.board[move.endRow][move.endCol - 2] = '--'  # xóa quân xe cũ

        # cập nhật luật nhập thành - bất cứ khi nào là lượt đi của vua hoặc xe
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        # Hãy chắc chắn rằng đây là nước đi hoàn tác
        move = self.moveLog.pop()
        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = move.pieceCaptured
        # Chuyển lượt chơi
        self.whiteToMove = not self.whiteToMove
        # Cập nhật vị trí của vua nếu cần
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.startRow, move.startCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.startRow, move.startCol)
        # Hoàn tác nước bắt tốt qua đường
        if move.isEnpassantMove:
            self.board[move.endRow][move.endCol] = '--'  # leave landing square blank
            self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enpassantPossible = (move.endRow, move.endCol)
        # hoàn tác lại nước ốt đầu tiên (đi 2 ô)
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ()
        # hoàn tác lại nhập thành
        self.castleRightsLog.pop()  # loại bỏ các quyền của nhập thành mới khỏi động thái đang hoàn tác
        self.currentCastlingRight = self.castleRightsLog[-1]  # đặt luật nhập thành hiện tại vào cuối danh sách
        # hoàn tác lại nước đi nhập thành
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # nước đi nhập thành phía bên vua
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                self.board[move.endRow][move.endCol - 1] = '--'
            else:  # phía bên hậu
                self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
        self.checkMate = False
        self.staleMate = False

    # cập nhật luật nhập thành khi thi triển nươc đi
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqk = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # quân xe trái
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # quân xe phải
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # quân xe trái
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # quân xe phải
                    self.currentCastlingRight.bks = False

    '''
    Tất cả các nước đi được kiểm tra
    '''

    def getValidMoves(self):
        # Thuật toán cũ
        tempEnpassantPossible = self.enpassantPossible
        # sao chép luật nhập thành hiện tại
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # 1) Khởi tạo các nước đi có thể
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves, 'w')
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves, 'b')
        #2) Thực hiện từng bước đi trong danh sách nước đi
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # 3) Khởi tạo các nước đi của đối phương
            # 4) với mỗi nước đi của đối phương, xem vua của bạn có bị tấn công không
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 5) Nếu họ tấn công vua bạn, thì nước đi của mình bạn hợp lệ
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        # 1 trong 2 chiếu hết hoặc hòa
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    # Kiểm tra xem lượt của người chơi bất kì có vua bị chiếu không
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # Kiêm tra xem đối thủ có chiếm giữ ô chiếu không
    def squareUnderAttack(self, r, c):
        # Đổi về lượt đối thủ
        self.whiteToMove = not self.whiteToMove
        # lấy tất cả nước đi có thể của quân đối thủ
        oppMoves = self.getAllPossibleMoves()
        # Đổi lại về lượt của mình
        self.whiteToMove = not self.whiteToMove
        # Duyệt tất cả các ô có thể đi của đối thủ,
        # nếu ô chiếu có trong đó, trả true, không trả false
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    # Hàm tạo danh sách nước đi có thể của quân đang xét
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]

                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and (not self.whiteToMove)):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # whitepawnmoves
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))

                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # capture to the left
                if self.board[r - 1][c - 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.isEnpassantMove:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))

            if c + 1 <= 7:  # capture to the right
                if self.board[r - 1][c + 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.isEnpassantMove:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))

        else:  # quân đen di chuyển
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # capture to left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.isEnpassantMove:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # capture to right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.isEnpassantMove:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # trên , trái, dưới, phải
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # trên bàn cờ
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # chỗ trống hợp lệ
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # quân địch hợp lệ
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # quân của ta hợp lệ
                        break
                else:  # không có trên bàn cờ
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # trên bàn cờ
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # không phải là quân bên ta(chỗ trống hặc có quân địch)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 đường chéo
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):  # quân tịnh có thể đi chéo nhiều nhất là 7 ô
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # trên bàn cờ
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # chỗ trống hợp lệ
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # quân địch hợp lệ
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # quân của ta hợp lệ
                        break
                else:  # không có trên bàn cờ
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # trên bàn cờ
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # không phải là quân bên ta(chỗ trống hặc có quân địch)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastleMoves(self, r, c, moves, allyColor):
        if self.squareUnderAttack(r, c):
            return  # không thể nhập thành nếu đang bị chiếu
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves, allyColor)

    def getKingsideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class Move():
    # Chuyển các ký tự tọa độ ở cạnh bàn cờ thành các chỉ số trong ma trận hai chiều và ngược lại
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSquare, endSquare, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
                self.pieceMoved == 'bp' and self.endRow == 7)
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # nước đi nhập thành
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotaion(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
