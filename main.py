__author__ = 'Dzirrot, Andrew Chumakin'
import webview
from threading import Thread
from multiprocessing import Process, Queue

import dbus
import dbus.mainloop.glib
from gi.repository import GLib


class DbusReader:
    INTERFACE = 'org.gnome.Shell'
    PATH = '/org/gnome/Shell'

    def __init__(self, queue: Queue):
        self.queue = queue

    def parse_signal(self, code, _):
        print(f'### got a signal: {code}: DBUS')
        self.queue.put(code)

    def run(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_session = dbus.SessionBus()
        object_ = bus_session.get_object(self.INTERFACE, self.PATH)
        object_.connect_to_signal("AcceleratorActivated", self.parse_signal, dbus_interface=self.INTERFACE)
        loop = GLib.MainLoop()
        print('LOOOOP RUN')
        loop.run()


class KeyboardLayout(Thread):
    JS_KEYBOARD_EVENT = '''document.dispatchEvent(new KeyboardEvent('keypress', {}));'''

    def __init__(self, window, queue: Queue):
        super().__init__()
        self.queue = queue
        self.window = window
        self.play_pause = self.JS_KEYBOARD_EVENT.format({'keyCode': 32, 'which': 32})
        self.prev = self.JS_KEYBOARD_EVENT.format({'keyCode': 75, 'which': 75})
        self.next = self.JS_KEYBOARD_EVENT.format({'keyCode': 76, 'which': 76})

    def press_next(self):
        self.window.evaluate_js(self.next)

    def press_prev(self):
        self.window.evaluate_js(self.prev)

    def press_play_pause(self):
        self.window.evaluate_js(self.play_pause)

    def parse_signal(self, signal):
        print(f'GOT A SIGNAL: {signal}')
        if signal == 152:
            self.press_prev()
        elif signal == 149:
            self.press_play_pause()
        elif signal == 153:
            self.press_next()
        else:
            pass

    def run(self):
        while True:
            print('try to get signal')
            print(queue.empty())
            self.parse_signal(self.queue.get())
            print('after got signal')


class WindowWebview:
    URL = "https://passport.yandex.com/auth?origin=music_button-header&retpath=https%3A%2F%2Fmusic.yandex.com%2Fhome"

    def __init__(self):
        """Конструктор."""
        self.window = webview.create_window(
            "Ya.Music",
            url=self.URL
        )

    @staticmethod
    def start():
        """Запуск окна webview."""
        webview.start(debug=True)


if __name__ == '__main__':
    queue = Queue()
    window_webview = WindowWebview()

    # Got HotKeys
    proc = Process(target=DbusReader(queue).run, args=())
    proc.start()

    # Work with hotkeys
    KeyboardLayout(window=window_webview.window, queue=queue).start()

    # Start Window
    window_webview.start()
