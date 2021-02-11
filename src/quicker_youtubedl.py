import sys
import subprocess
import logging
from pathlib import Path, PureWindowsPath
from PySide2 import QtWidgets, QtGui


logging.basicConfig(level=logging.DEBUG)


class mk_QuickerYoutubeDL(QtWidgets.QWidget):

    _VERSION = '0.0.2'
    _TMP_DIR = 'youtube-dl-temp'

    def __init__(self, drive_combox_box_index=1, audio_centric=False):
        super(mk_QuickerYoutubeDL, self).__init__(parent=None)
        self.setWindowTitle('mk Quicker youtube-dl v{}'.format(mk_QuickerYoutubeDL._VERSION))
        self.setWindowIcon(QtGui.QIcon((Path(__file__).parent / 'img/mk_quicker_youtubedl_icon.png').as_posix()))
        # self.setFixedSize(350, 70)

        self.create_widgets(drive_combox_box_index, audio_centric) # default is D: drive
        self.create_layouts()
        self.create_connections()

    def create_widgets(self, drive_combox_box_index, audio_centric):
        self.drive_combo_box = QtWidgets.QComboBox()
        self.drive_combo_box.addItems(('C:', 'D:', 'E:', 'F:', 'G:'))
        self.drive_combo_box.setCurrentIndex(drive_combox_box_index)

        self.audio_only_cb = QtWidgets.QCheckBox('Audio Only')
        self.audio_only_cb.setChecked(audio_centric)

        self.url_le = QtWidgets.QLineEdit()
        self.url_le.setMinimumWidth(280)

        self.show_results_btn = QtWidgets.QPushButton('>>>')        

        max_btn_width = 50
        self.drive_combo_box.setMaximumWidth(max_btn_width)
        self.show_results_btn.setMaximumWidth(max_btn_width)
        self.show_results_btn.setStyleSheet('font-size: 8px;')
            
    def create_layouts(self):
        main_lo = QtWidgets.QFormLayout(self)
        
        main_lo.addRow(self.audio_only_cb, self.show_results_btn)
        main_lo.addRow(self.url_le, self.drive_combo_box)

    def create_connections(self):
        self.url_le.returnPressed.connect(self.parse_url)
        self.show_results_btn.clicked.connect(self.show_results)

    def prepare_destination(self, drive):
        dst_dir = Path('{}\{}'.format(drive, mk_QuickerYoutubeDL._TMP_DIR))
        # Make sure the output folder exists
        if not dst_dir.exists():
            try:
                dst_dir.mkdir()
            except Exception as e:
                logging.error('Unable to create "{}" folder in the drive specified due to: {}'.format(mk_QuickerYoutubeDL._TMP_DIR, e))
                return None
        return dst_dir

    def show_results(self):
        chosen_drive = self.drive_combo_box.currentText()
        dst_dir = self.prepare_destination(chosen_drive)
        # Show explorer at dst_dir
        subprocess.Popen(['explorer', str(PureWindowsPath(dst_dir))])

    def parse_url(self):
        chosen_drive = self.drive_combo_box.currentText()
        pasted_url = self.url_le.text()
        audio_only = self.audio_only_cb.isChecked()

        if pasted_url:
            self.do_youtubedl(chosen_drive, pasted_url, audio_only)

    def do_youtubedl(self, drive, url, audio_only=False):
        """
        :param str url:
        :param str drive:
        """
        dst_dir = self.prepare_destination(drive)

        if dst_dir:  # valid drive output
            # Ignore errors and force continue
            youtubedl_cmd = [
                "youtube-dl", 
                "-ci"
            ]
            
            # Config output file name(s)
            # First see if the URL pasted is a playlist
            playlist_mode = url.find('&list=') != -1
            
            if not playlist_mode:
                # Single video
                dst_dir = "{}\%(title)s.%(ext)s".format(str(PureWindowsPath(dst_dir)))    
            else:
                # Video playlist
                dst_dir = "{}\%(playlist_index)s-%(title)s.%(ext)s".format(str(PureWindowsPath(dst_dir)))

            if audio_only:
                youtubedl_cmd.extend(
                    (
                        "-f", 
                        "140"
                    )
                )

            # Output specifiers and the URL as final arguments
            youtubedl_cmd.extend(
                (
                    "-o",
                    dst_dir, 
                    url
                )
            )
            
            logging.debug('YOUTUBE-DL youtubedl_cmd: {}'.format(str(youtubedl_cmd)))
            
            try:
                subprocess.call(youtubedl_cmd)
            except Exception as e:
                logging.warning('Unable to perform video|audio download due to: {}'.format(e))


if __name__ == '__main__':

    app = QtWidgets.QApplication()

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Called from .exe
        # mk_QuickerYoutubeDLInst = mk_QuickerYoutubeDL()  # default drive
        mk_QuickerYoutubeDLInst = mk_QuickerYoutubeDL(audio_centric=True)  # for Hue
    else:
        # Devving
        mk_QuickerYoutubeDLInst = mk_QuickerYoutubeDL()  # set to G: drive

    mk_QuickerYoutubeDLInst.show()
    sys.exit(app.exec_())
