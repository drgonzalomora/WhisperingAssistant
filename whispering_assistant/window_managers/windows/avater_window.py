import time
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

from whispering_assistant.window_managers.windows.base_window_template import BaseWindowTemplate


class InfoWindow(BaseWindowTemplate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def initUI(self, title="Info", width=300, height=300,
               media_path="/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/videos/ARA_AVATAR.mp4"):
        self.setWindowTitle(title)
        self.setGeometry(0, 0, width, height)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.text_label = QLabel(self.central_widget)
        self.layout.addWidget(self.text_label)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVolume(0)
        self.video_widget = QVideoWidget(self.central_widget)
        self.video_widget.setMinimumSize(width, height)
        self.layout.addWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)

        # Connect mediaStatusChanged signal to the loop_video method
        self.media_player.mediaStatusChanged.connect(self.loop_video)
        self.media_player.error.connect(self.handle_error)
        self.hide()

    def set_content(self, title, text,
                    media_path="/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/videos/ARA_AVATAR.mp4"):
        self.setWindowTitle(title)
        self.text_label.setText(text)

        if media_path is not None:
            media_content = QMediaContent(QUrl.fromLocalFile(media_path))
            self.media_player.setMedia(media_content)
            self.media_player.play()

        time.sleep(0.1)
        self.show()

    def hide_stop(self):
        self.media_player.stop()
        self.hide()

    def loop_video(self, status):
        if status == QMediaPlayer.EndOfMedia:
            print("End of media reached, looping video...")
            self.media_player.setPosition(0)
            self.media_player.play()
        elif status == QMediaPlayer.InvalidMedia:
            print("Invalid media")
        elif status == QMediaPlayer.BufferedMedia:
            print("Media buffered")
        elif status == QMediaPlayer.LoadingMedia:
            print("Loading media")
        elif status == QMediaPlayer.StalledMedia:
            print("Media stalled")
        elif status == QMediaPlayer.UnknownMediaStatus:
            print("Unknown media status")

    def handle_error(self):
        print("Error: " + self.media_player.errorString())
