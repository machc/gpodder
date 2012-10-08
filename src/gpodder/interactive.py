# todo: sort by date
# todo: download %

import curses
import locale
#todo: maybe use threading?
import thread

class Interactive(object):
    """
    Interactive command-line user interface. This class helps using gPodder in command-line mode, displaying a navigable list of podcasts and episodes, allowing the user to execute actions on them. 
    """

    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.code = locale.getpreferredencoding()
        self.screen = curses.initscr()
        curses.noecho()
        self.screen.keypad(1)
        self.max_items = self.screen.getmaxyx()[0]-2 # maximum number of items on screen
        self.first_item = 1 # id of first item on screen
        self.selected_id = 1 # id of selected item
        self.selected_episode = None # episode selected
    
    def update_screen(self, env):
        self.screen.clear()
        self.screen.border(0)
        count = 1 # id of episode
        for podcast in env.client.get_podcasts():
            for episode in podcast.get_episodes():
                if episode.is_new and \
                        (count <= self.first_item + self.max_items - 1) and \
                        (count >= self.first_item):
                    if count == self.selected_id:
                        attr = curses.A_REVERSE
                        self.selected_episode = episode
                    else:
                        attr = curses.A_NORMAL
                    line = (' ' + podcast.title + ' - ' + episode.title)\
                        .encode(self.code, 'ignore')
                    self.screen.addstr(count + 1 - self.first_item, 1, line, attr)
                count += 1
        self.screen.refresh()    
        
    def run(self, env):
        while True:
            self.update_screen(env)
            key = self.screen.getch()
            # down
            if (key == curses.KEY_DOWN):
                if (self.selected_id == self.first_item + self.max_items - 1):
                    self.first_item += 1
                # todo: verifiy if is the last episode
                self.selected_id += 1
            # up
            if (key == curses.KEY_UP):
                if (self.selected_id == self.first_item) and \
                        (self.first_item > 1):
                    self.first_item -= 1
                if (self.selected_id > 1):
                    self.selected_id -= 1
            # todo: implement pg up and down
            # pg down
#            if (key == curses.KEY_PPAGE):

            # pg up
#            if (key == curses.KEY_NPAGE):

            # todo: implement info
            # show_episotde_shownotes
            # info
#            if key == ord('i'):
                # todo: How to get correct description?
                # todo: show description in new window
                
            # download
            if key == ord('d'):
                thread.start_new_thread(\
                    self.selected_episode.download, ())
                
            # quit
            if key == ord('q'):
                self.terminate()
                break
    
    def terminate(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()
