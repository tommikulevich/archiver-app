import sys
import argparse
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo
from PyQt5.QtWidgets import QApplication

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

from archive_app_qt.archive_app import ArchiveAppQt
if GTK_AVAILABLE:
    from archive_app_gtk.archive_app import ArchiveAppGtk

def run_qt():
    app = QApplication(sys.argv)
    
    archive_app = ArchiveAppQt()
    archive_app.show()
    sys.exit(app.exec_())
    
def run_gtk():
    if GTK_AVAILABLE:
        win = ArchiveAppGtk()
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    else:
        print("GTK is not supported (you must install the appropriate libraries).")
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', choices=['qt', 'gtk'], default='qt', help="Choose GUI: 'qt' or 'gtk'")
    args = parser.parse_args()

    if args.gui == 'qt':
        run_qt()
    elif args.gui == 'gtk':
        run_gtk()