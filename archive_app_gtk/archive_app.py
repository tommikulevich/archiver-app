import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from archive_app_gtk.archive_window import ArchiveWindowGtk
from archive_app_gtk.unarchive_window import UnarchiveWindowGtk


class ArchiveAppGtk(Gtk.Window):
    def __init__(self):
        # Some window initialization
        super().__init__(title='Archiwizator z szyfrowaniem')
        self.set_size_request(600, 400)
        self.set_border_width(10)
        
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        # Menu bar with "Information"
        mb = Gtk.MenuBar()
        aboutitem = Gtk.MenuItem.new_with_label("Informacja")
        aboutitem.connect("button-press-event", self.on_about_activated)
        mb.append(aboutitem)
        box_outer.pack_start(mb, False, False, 0)

        # File browser
        self.file_chooser = Gtk.FileChooserWidget(action=Gtk.FileChooserAction.OPEN)
        self.file_chooser.set_select_multiple(True)
        box_outer.pack_start(self.file_chooser, True, True, 0)
        
        # Main buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_outer.pack_start(button_box, False, False, 0)

        btn_archive = Gtk.Button.new_with_label("Zarchiwizować")
        btn_archive.connect("clicked", self.on_archive_clicked)
        button_box.pack_start(btn_archive, False, False, 0)
        
        btn_unarchive = Gtk.Button.new_with_label("Rozpakować")
        btn_unarchive.connect("clicked", self.on_unarchive_clicked)
        button_box.pack_start(btn_unarchive, False, False, 0)
    
    def on_about_activated(self, widget, event):
        # Show info about application from file
        about_filename = "data/about.txt"
        
        about = "Archiwizator z szyfrowaniem."
        if os.path.exists(about_filename):
            with open(about_filename, 'r', encoding="utf-8") as file:
                about = file.read()
        
        about_dialog = Gtk.MessageDialog(
            transient_for=self, 
            flags=0,
            message_type=Gtk.MessageType.INFO, 
            buttons=Gtk.ButtonsType.OK, 
            text="Opis aplikacji"
        )
        about_dialog.format_secondary_text(about)
        about_dialog.run()
        about_dialog.destroy()

    def on_archive_clicked(self, widget):
        # Get selected files
        selected_files = self.file_chooser.get_filenames()
        print("[Archive] Selected files", selected_files)
        
        # Check if any file was selected
        if not selected_files:
            dialog = Gtk.MessageDialog(
                transient_for=self, 
                flags=0,
                message_type=Gtk.MessageType.WARNING, 
                buttons=Gtk.ButtonsType.OK,
                text="Błąd"
            )
            dialog.format_secondary_text("Nie wybrano plików.")
            dialog.run()
            dialog.destroy()
            return
        
        # Open Archive window
        archive_window = ArchiveWindowGtk(selected_files, parent=self)
        archive_window.show_all()
        self.set_sensitive(False)
        archive_window.connect("delete-event", self.on_child_delete)

    def on_unarchive_clicked(self, widget):
        # Get selected files
        selected_files = self.file_chooser.get_filenames()
        print("[Unarchive] Selected files", selected_files)
        
        # Check if any file was selected
        if not selected_files:
            dialog = Gtk.MessageDialog(
                transient_for=self, 
                flags=0,
                message_type=Gtk.MessageType.WARNING, 
                buttons=Gtk.ButtonsType.OK,
                text="Błąd"
            )
            dialog.format_secondary_text("Nie wybrano plików.")
            dialog.run()
            dialog.destroy()
            return
        
        # Check archive extensions
        allowed_extensions = {".zip", ".7z", ".tar", ".tar.gz", ".tar.bz2", ".tar.xz"}
        extensions = {"." + file.split('.')[-1].lower() for file in selected_files}
        if not extensions.issubset(allowed_extensions):
            dialog = Gtk.MessageDialog(
                transient_for=self, 
                flags=0,
                message_type=Gtk.MessageType.WARNING, 
                buttons=Gtk.ButtonsType.OK,
                text="Błąd"
            )
            dialog.format_secondary_text("Jeśli chcesz rozpakować pliki, "
                "muszą one mieć rozszerzenia: .zip, .7z lub .tar")
            dialog.run()
            dialog.destroy()
            return 
        
        # Open Unarchive window
        unarchive_window = UnarchiveWindowGtk(selected_files, parent=self)
        unarchive_window.show_all()
        self.set_sensitive(False)
        unarchive_window.connect("delete-event", self.on_child_delete)

    def on_child_delete(self, widget, event):
        self.set_sensitive(True)
