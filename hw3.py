from typing import List, Optional, Tuple
from random import randint

Coordinates = List[Tuple[int, int]]
Board = List[List[str]]


def new_playground() -> Board:
    playground = []
    for i in range(3):
        playground.append(['  '] * 3)
    return playground


def get(playground: Board, row: int, col: int) -> str:
    return playground[row][col]


def update_board(playground: Board, symbol: str) -> None:
    for row in range(3):
        for col in range(3):
            if playground[row][col][0] == symbol:
                playground[row][col] = symbol + \
                                       str(int(playground[row][col][1]) + 1)
                if playground[row][col][1] == '4':
                    playground[row][col] = '  '


def put(playground: Board, row: int,
        col: int, symbol: str) -> bool:
    if not playground[row][col] == '  ':
        return False
    update_board(playground, symbol)
    playground[row][col] = symbol + '1'
    return True


def draw(playground: Board) -> None:
    line_separator = ("   " + 3 * "+--" + "+")
    print(line_separator)

    for x in range(3):
        print(" " + str(x), end=" ")

        for y in range(3):
            print('|{}'.format(playground[x][y]), end='')
        print('|')
        print(line_separator)
    print("   ", end="  ")

    for letter in range(ord('A'), ord('C') + 1):
        print(chr(letter), end="  ")
    print()


def get_coordinates(playground: Board, symbol: str, get_hint: bool = False) \
        -> Tuple[Coordinates, Optional[Tuple[int, int]]]:
    coords = []
    previous = None
    for row in range(len(playground)):
        for col in range(len(playground[row])):
            if playground[row][col][0] != symbol:
                continue
            if get_hint:
                if playground[row][col][1] == '3':
                    previous = row, col
                    continue
            coords.append((row, col))
    return coords, previous


def horizontal_vertical(coords: Coordinates, horizontal: bool = True) -> bool:
    mode = 0 if horizontal else 1
    for coord in range(len(coords) - 1):
        if coords[coord][mode] != coords[coord + 1][mode]:
            return False
    return True


def diagonal(coords: Coordinates) -> bool:
    is_main_diagonal = all(x == y for x, y in coords)
    is_other_diagonal = all((x + y) == 2 for x, y in coords)
    return is_main_diagonal or is_other_diagonal


def who_won(playground: Board) -> Optional[str]:
    winer: List[str] = []

    for symbol in ['O', 'X']:
        coords, _ = get_coordinates(playground, symbol)
        if len(coords) == 3:
            if diagonal(coords):
                return symbol
            elif horizontal_vertical(coords):
                winer.append(symbol)
            elif horizontal_vertical(coords, horizontal=False):
                winer.append(symbol)
    if len(winer) == 2:
        return 'invalid'
    elif len(winer) == 0:
        return None
    return winer[0]


def get_free_position(pos1: int, pos2: int) -> int:
    return 3 - pos1 - pos2


def hint(playground: Board, symbol: str) -> Optional[Tuple[int, int]]:
    coords, previous = get_coordinates(playground, symbol, get_hint=True)
    if len(coords) < 2:
        return None

    (row1, col1), (row2, col2) = coords
    position = row1, col1

    if row1 == row2:
        position = row1, get_free_position(col1, col2)
    elif col1 == col2:
        position = get_free_position(row1, row2), col1
    elif row1 == col1 and row2 == col2:
        pos = get_free_position(row1, row2)
        position = pos, pos
    elif (row1 + col1) == 2 and (row2 + col2) == 2:
        position = abs(row1 - col1), abs(row2 - col2)
        position = (1, 1) if position == (2, 2) else position
    row, col = position
    return position if get(playground, row, col) == '  ' \
                       and position != previous else None


def player(board: Board) -> None:
    player_row, player_col = -1, -1
    possible_move = hint(board, 'X')
    if possible_move is not None:
        posible_move_str = str(possible_move[0]) + chr(possible_move[1] + 65)
        print('winning position : ', posible_move_str)

    valid_position = False
    while not valid_position:
        player_move = input('Enter your move: ')
        player_row = int(player_move[0])
        player_col = ord(player_move[1]) - 65
        valid_position = 0 <= player_row < 3 and 0 <= player_col < 3
        if not valid_position:
            print('invalid coordinates, try again')
    put(board, player_row, player_col, 'X')
    return


def computer(board: Board) -> None:
    comp_winner_position = hint(board, 'O')
    player_winner_position = hint(board, 'X')
    comp_position = comp_winner_position
    
    if comp_winner_position is None:
        free_coordinates, _ = get_coordinates(board, ' ')
        if player_winner_position is not None:
            comp_position = player_winner_position
        elif (1, 1) in free_coordinates:
            comp_position = (1, 1)
        else:
            index = randint(0, len(free_coordinates) - 1)
            comp_position = free_coordinates[index]

    assert comp_position is not None
    put(board, comp_position[0], comp_position[1], 'O')
    return


def print_result(winner: str, counter: int) -> None:
    print("\nGAME OVER")
    print(40 * '-')
    if winner == 'O':
        print(f"YOU LOST in {counter} moves")
    elif winner == 'invadid':
        print('')
    else:
        print(f"Congratulation, YOU WIN in {counter} moves")
    return


def game() -> None:
    print(40 * '-')
    print("WELCOME, we play Tic-Tac-Toe\n"
          '\n-> you are X and computer plays with O \n'
          '-> input your moves in form 1B, 2A...')
    print(40 * '-')

    board = new_playground()
    draw(board)
    counter = 1
    winner = who_won(board)
    while winner is None:
        print('ROUND ', counter)
        player(board)
        draw(board)
        computer(board)
        draw(board)
        counter += 1
        winner = who_won(board)
    print_result(winner, counter)
    return

game()
if __name__ == '__main__':
    pass
