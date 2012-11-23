# todo: change TUI from curses to urwid
# todo: show info
    #todo: dehtmlize description 
    # todo: sort by date
    # todo: download %

import urwid
import locale
#todo: maybe use threading?
import thread

# download
# if key == ord('d'):
#             thread.start_new_thread(\
    #                 self.selected_episode.download, ())

class Interactive(object):
    """
    Interactive command-line user interface. This class helps using gPodder in command-line mode, displaying a navigable list of podcasts and episodes, allowing the user to execute actions on them. 
    """
    def __init__(self, env):
        self.episodes = None
        self.env = env
    
    def get_episodes_list(self):
        episodes = []
        for podcast in self.env.client.get_podcasts():
            for episode in podcast.get_episodes():
                if episode.is_new:
                    episodes.append(episode)
        self.episodes = episodes

    # class EpisodeListBox(urwid.ListBox):
    #     def keypress(self, size, key):
    #         if key=='i':
                

    def make_episodes_listbox(self, title):
        body = [urwid.Text(title), urwid.Divider()]
        for episode in self.episodes:
            podcast_title = episode._episode.parent.title
            button = urwid.Button(podcast_title + ': ' +episode.title)
            urwid.connect_signal(button, 'click', self.show_info, episode)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        return self.EpisodeListBox(urwid.SimpleFocusListWalker(body))
        
    def show_info(self, episode):
        """
        Show episode description in a dialog box
        """
        urwid.Text(episode.description)

    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        

    def run(self):
        self.get_episodes_list()
        ep_listbox = self.make_episodes_listbox('New episodes')

        main = urwid.Padding(ep_listbox, left=2, right=2)
        urwid.MainLoop(main, unhandled_input=self.exit_on_q, \
                           palette=[('reversed', 'standout', '')]).run()

