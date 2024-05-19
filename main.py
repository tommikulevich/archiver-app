import sys
import argparse
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QApplication

from archive_app_qt.archive_app import ArchiveAppQt
from archive_app_gtk.archive_app import ArchiveAppGtk


def run_qt():
    app = QApplication(sys.argv)
        
    translator = QtCore.QTranslator()
    if translator.load(QtCore.QLocale('pl_PL'), 'qtbase', '_', 
            QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)):
        app.installTranslator(translator)
    
    archive_app = ArchiveAppQt()
    archive_app.show()
    sys.exit(app.exec_())
    
def run_gtk():
    win = ArchiveAppGtk()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', choices=['qt', 'gtk'], default='qt', help="Choose GUI: 'qt' or 'gtk'")
    args = parser.parse_args()

    if args.gui == 'qt':
        run_qt()
    elif args.gui == 'gtk':
        run_gtk()
