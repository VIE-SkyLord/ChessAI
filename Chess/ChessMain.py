# File xử lý đầu vào của người dùng và hiển thị trạng thái trò chơi hiện tại

import pygame as p
from Chess import ChessEngine

WIDTH = HEIGHT = 512
DIMEMSION = 8
SQUARE_SIZE = WIDTH // DIMEMSION
MAX_FPS = 15
IMAGES = {}


# Khởi tạo thư viện toàn cục cho ảnh
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        try:
            image_path = "images/" + piece + ".png"
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
    loadImages()
    running = True
    # Không ô cờ nào được chọn, theo dõi lần click cuối của người dùng (tọa độ (x,y))
    squareSelected = ()
    # giữ việc theo dõi lần nhấn của người chơi (2 cặp tọa độ(6,4), (4,4))
    playerClicks = []
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
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
                #Sau khi click 2 lần
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0],playerClicks[1], gs.board)
                    print(move.getChessNotaion())
                    gs.makeMove(move)
                    # Đặt lại click của người chơi
                    squareSelected = ()
                    playerClicks = []

        drawGameState(screen, gs)  # Move this outside of the event loop
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    # vẽ ô lên bàn cờ
    drawBoard(screen)
    # thêm màu sáng vào ô nước khả dụng của quân cờ
    # vẽ quân cờ lên trên bàn cờ
    drawPieces(screen, gs.board)


# Vẽ ô trên bàn cờ, ô ở góc trái trên cùng
def drawBoard(screen):
    colors = [p.Color("lightgray"), p.Color("darkgreen")]
    for r in range(DIMEMSION):
        for c in range(DIMEMSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawPieces(screen, board):
    for row in range(DIMEMSION):
        for col in range(DIMEMSION):
            piece = board[row][col]
            if piece != "--":  # Check if the square is not empty
                screen.blit(IMAGES[piece], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


if __name__ == "__main__":
    main()
