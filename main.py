import sys
from trello import Trello

if __name__ == '__main__':
    try:
        obj = Trello()
        obj.login()
        obj.build_team()
        obj.create_new_board()
        obj.init_tasks()
        obj.rand_drag_all_cards()
    except Exception as e:
        print(f'{e.__class__.__name__}: {e}')
        sys.exit(1)
