# todo: improve info popups size/location
# todo: show date
# todo: show if episode was marked as old

import urwid
import locale
#todo: maybe use threading?
import thread
# for pretty pretting html episode info
import BeautifulSoup
import re

import download

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
        # sort episodes by date
        episodes.sort(reverse = True, key=lambda k: k._episode.published)
        self.episodes = episodes

    def make_episodes_listbox(self, title):
        body = [urwid.Text(title), urwid.Divider()]
        for episode in self.episodes:
            podcast_title = episode._episode.parent.title.encode('ascii', 'ignore')
            episode_title = episode.title.encode('ascii', 'ignore') 
            try:
                button = EpisodeButtonPopUp(podcast_title + ': ' + episode_title + ' - ' + episode._episode.pubdate_prop, episode, self.env)
            except: 
                button = EpisodeButtonPopUp('error in episode name', episode, self.env) 

            body.append(urwid.AttrMap(button, None, focus_map='selected'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def run(self):
        self.get_episodes_list()
        ep_listbox = self.make_episodes_listbox('New episodes')

        loop = urwid.MainLoop(ep_listbox,
                              unhandled_input=self.exit_on_q,
                              palette=[('selected', 'standout', ''),\
                                           ('downloading', 'bold', ''),\
                                           ('done', 'underline', '')],
                              pop_ups=True)
        loop.run()

class EpisodeButton(urwid.Button):
    signals = ['show_info']
    def __init__(self, label, episode, env):
        urwid.Button.__init__(self, label)
        self.episode = episode
        self.labelpart = label
        self.env = env
        self.task = download.DownloadTask(self.episode._episode, self.env.config)
        self.size = (80, 1)

    # give download status
    def _update_action(self, progress):
        progress = ' %3.0f%%' % (progress*100.,)
        cols = self.size[0]
        lblcols = len(self.labelpart)
        # 8 = <, >, 4 chars for progess + 4 spaces
        nspaces = cols - lblcols - 10
        self.set_label(('downloading', self.labelpart + ' '*nspaces + progress))
        # todo: need to somehow call loop.draw_screen here?

    def keypress(self, size, key):
        key = super(EpisodeButton, self).keypress(size, key)
        # update widget size for positioning text
        self.size = size
        # show info
        if key=='i':
            self._emit("show_info")
        # download
        elif key == 'd':
            self.task.add_progress_callback(self._update_action)
            self.task.status = download.DownloadTask.QUEUED
            thread.start_new_thread(self.task.run, ())
        # toggle read/unread
        elif key == 'm':
            if self.episode.is_new:
                self.episode._episode.mark_old()
                self.set_label(('done', self.labelpart))
            else:
                self.episode._episode.mark_new()
                self.set_label(('selected', self.labelpart))
        else:
            return key

class EpisodeButtonPopUp(urwid.PopUpLauncher):
    def __init__(self, label, episode, env):
        self.__super.__init__(EpisodeButton(label, episode, env))
        self.episode = episode
        urwid.connect_signal(self.original_widget, 'show_info',
            lambda button: self.open_pop_up())

    def create_pop_up(self):
        description = BeautifulSoup.BeautifulSoup(self.episode.description).getText(' ').encode('utf-8')
        pop_up = PopUpDialog(description)
        urwid.connect_signal(pop_up, 'close',
            lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left':10, 'top':1, 'overlay_width':60, 'overlay_height':30}

class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']
    def __init__(self, text):
        close_button = urwid.Button("close")
        urwid.connect_signal(close_button, 'click',
            lambda button:self._emit("close"))
        pile = urwid.Pile([urwid.Text(text), close_button])
        fill = urwid.Filler(urwid.LineBox(pile))
        self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))
