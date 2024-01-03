# File xử lý đầu vào của người dùng và hiển thị trạng thái trò chơi hiện tại

import pygame as p
from Chess import ChessEngine, SmartMoveFinder

WIDTH = HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}


# Khởi tạo thư viện toàn cục cho ảnh
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        image_path = "images/" + piece + ".png"
        try:
            IMAGES[piece] = p.transform.scale(p.image.load(image_path), (SQUARE_SIZE, SQUARE_SIZE))
            print(f"Successfully loaded image: {image_path}")
        except p.error as e:
            print(f"Error loading image {image_path}: {e}")


# Hàm chính nhận dữ liệu người dùng và cập nhật đồ họa
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    # Không ô cờ nào được chọn, theo dõi lần click cuối của người dùng (tọa độ (x,y))
    squareSelected = ()
    # giữ việc theo dõi lần nhấn của người chơi (2 cặp tọa độ(6,4), (4,4))
    playerClicks = []
    gameOver = False
    # nếu là người chơi cầm quân trắng, trẻ về true, còn nếu là máy thì trả về false
    playerOne = True
    # tương tự như vậy với quân đen
    playerTwo = False
    while running:
        #lượt của người chơi trắng hoặc của người chơi đen
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    # vị trí chuột tọa độ 2 chiều x,y
                    location = p.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    # Người chơi đã nhấn vào ô 2 lần
                    if squareSelected == (row, col):
                        squareSelected = ()
                        playerClicks = []
                    else:
                        squareSelected = (row, col)
                        # Thêm cả 2 lần click thứ nhất và thứ 2
                        playerClicks.append(squareSelected)
                    # Sau khi click 2 lần
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotaion())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                # Đặt lại click của người chơi
                                animate = True
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                elif e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        # Tìm kiếm nước đi của AI
        # lượt của người máy trắng hoặc của người máy đen
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animatedMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        # Đưa cái này khổi sự kiện loop
        drawGameState(screen, gs, validMoves, squareSelected)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black win by checkmate')
            else:
                drawText(screen, 'White win by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()


def highlightSquare(screen, gs, validMoves, squareSelected):
    if squareSelected != ():
        r, c = squareSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # transpenacy value ->0 transparent;255 opague
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
            # Làm sáng các ô khác từ ô đó
            s.fill(p.Color('orange'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))


def drawGameState(screen, gs, validMoves, squareSelected):
    # vẽ ô lên bàn cờ
    drawBoard(screen)
    # thêm màu sáng vào ô nước khả dụng của quân cờ
    highlightSquare(screen, gs, validMoves, squareSelected)
    # vẽ quân cờ lên trên bàn cờ
    drawPieces(screen, gs.board)


# Vẽ ô trên bàn cờ, ô ở góc trái trên cùng
def drawBoard(screen):
    global colors
    colors = [p.Color("lightgray"), p.Color("darkgreen")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":  # Check if the square is not empty
                screen.blit(IMAGES[piece], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def animatedMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # Frame to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
