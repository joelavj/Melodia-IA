from textual.app import App

from tests.screens.home_screen import HomeScreen

class MelodiaApp(App):
    TITLE = "Melodia IA"
    CSS_PATH = "tests/css/app.tcss"

    def on_mount(self)->None:
        self.push_screen(HomeScreen())

if __name__ == '__main__':
    MelodiaApp().run()