__author__ = 'Dzirrot, Andrew Chumakin'

import webview
from threading import Thread

from Xlib.display import Display
from Xlib import X
from Xlib.ext import record
from Xlib.protocol import rq


class KeyboardLayout(Thread):
    """Модуль для работы с горячими клавишами."""
    JS_KEYBOARD_EVENT = '''document.dispatchEvent(new KeyboardEvent('keypress', {}));'''

    def __init__(self, window):
        """
        Конструктор, для нормальной работы нужен экземпляр окна в котором будет выполняться эмуляция горячих клавиш.
        """
        super().__init__()
        self.window = window
        self.play_pause = self.JS_KEYBOARD_EVENT.format({'keyCode': 32, 'which': 32})
        self.prev = self.JS_KEYBOARD_EVENT.format({'keyCode': 75, 'which': 75})
        self.next = self.JS_KEYBOARD_EVENT.format({'keyCode': 76, 'which': 76})

        self.disp = None
        self.events = {
            173: self.press_prev,
            172: self.press_play_pause,
            171: self.press_next
        }

    def press_next(self):
        """Эмуляция нажатия next."""
        self.window.evaluate_js(self.next)

    def press_prev(self):
        """Эмуляция нажатия previous."""
        self.window.evaluate_js(self.prev)

    def press_play_pause(self):
        """Эмуляция нажатия play/pause."""
        self.window.evaluate_js(self.play_pause)

    def do_nothing(self):
        """Заглушка для ничего не делания."""
        pass

    def parse_signal(self, signal):
        """Разбор полученных сигналов."""
        data = signal.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, self.disp.display, None, None)
            if event.type == X.KeyPress:
                self.events.get(event.detail, self.do_nothing)()

    def run(self):
        """Метод по мониторингу нажатия клавиш."""
        # Обратимся к текущему окну.
        self.disp = Display()
        root = self.disp.screen().root
        ctx = self.disp.record_create_context(
            0,
            [record.AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                'device_events': (X.KeyReleaseMask, X.ButtonReleaseMask),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }])
        self.disp.record_enable_context(ctx, self.parse_signal)
        self.disp.record_free_context(ctx)
        while True:
            root.display.next_event()


class WindowWebview:
    """Модуль по работе с окном приложения."""
    URL = "https://passport.yandex.com/auth?origin=music_button-header&retpath=https%3A%2F%2Fmusic.yandex.com%2Fhome"

    def __init__(self):
        """Конструктор."""
        self.window = webview.create_window(
            "Ya.Music",
            url=self.URL
        )

    @staticmethod
    def start():
        """Запуск окна плеера."""
        webview.start(debug=True)


if __name__ == '__main__':
    window_webview = WindowWebview()
    # Поток по работе с горячими клавишами.
    KeyboardLayout(window=window_webview.window).start()
    # Запуск приложения
    window_webview.start()
