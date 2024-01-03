""""
        # Thuật toán cải tiến
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndCheck()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            # Có 1 quân chiếu thì ngăn đường chiếu hoặc di chuyển vua
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                # Để chặn đường chiếu cần phải đưa 1 quân cờ vào 1 ô giữa quân địch và vua
                # Thông tin về chiếu
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                # Quân địch dẫn tới chiếu
                pieceChecking = self.board[checkRow][checkCol]
                # Các ô mà quân cờ có thể di chuyển tới
                validSquares = []
                # Nếu là quân mã. Phải ăn Mã hoặc đi vua, không quân nào có thể chặn đường chiếu
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        # check[2] và check[3] là hướng chiếu
                        validSquare = (kingRow + check[2] + i, kingCol + check[3] + i)
                        validSquares.append(validSquare)
                        # kết thúc ô đường chiếu
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            # Chiếu đôi
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        # không bị chiếu thì các nước đi đều ổn
        else:
            moves = self.getAllPossibleMoves()

        return moves
"""
"""
    def checkForPinsAndCheck(self):
        # Số ô quân đang bị ghim, và bị ghim từ đâu
        pins = []
        # Số ô kẻ địch đang check
        checks = []
        inCheck = False
        if self.whiteToMove:
            enermyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enermyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            # làm mới Ghim quân
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        # chỉ có 1 quân cờ đồng minh bị ghim
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        # có 2 quân cờ đồng minh thì bỏ ghim
                        else:
                            break
                    elif endPiece[0] == enermyColor:
                        type = endPiece[1]
                        # 5 tất cả điều có thể xảy ra ở đây trong điều kiện phức tạp
                        # 1) nước đi dấu + của từ vua và xe
                        # 2) nước đi dấu x của từ vua và tượng
                        # 3) 1 ô nước đi dấu x của vua, tốt
                        # 4) mọi hướng và quân cờ là hậu
                        # 5) mọi hướng 1 ô cờ và quân là vua
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enermyColor == 'w' and 6 <= j <= 7) or (
                                        enermyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            # nếu không có quân cản thì là chiếu
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            # nếu có quân cản thì là ghim quân
                            else:
                                pins.append(possiblePin)
                                break
                        # quân địch không chiếu
                        else:
                            break
        # kiểm tra cho quân mã chiếu
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enermyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks
"""