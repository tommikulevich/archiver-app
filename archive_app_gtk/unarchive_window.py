import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from archive_app_gtk.worker import WorkerGtk


class UnarchiveWindowGtk(Gtk.Window):
    def __init__(self, selected_files, parent=None):
        # Some window initialization
        super().__init__(title="Unarchive files")
        self.selected_files = selected_files
        
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_border_width(10)
        self.set_default_size(450, 250)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Delete files checkbox
        self.check_delete_files = Gtk.CheckButton(label="Delete input files after completion")
        vbox.pack_start(self.check_delete_files, True, True, 0)

        # Password
        self.entry_password = Gtk.Entry()
        self.entry_password.set_placeholder_text("Decryption password (optional).")
        self.entry_password.set_visibility(False)
        vbox.pack_start(self.entry_password, True, True, 0)

        # Destination folder label and button
        self.folder_label = Gtk.Label(label="Destination folder: None selected")
        self.folder_label.set_xalign(0)
        
        button_choose_folder = Gtk.Button(label="Choose folder")
        button_choose_folder.connect("clicked", self.choose_dest_folder, self.folder_label)
        vbox.pack_start(button_choose_folder, True, True, 0)
        vbox.pack_start(self.folder_label, True, True, 0)

        # Start button
        self.button_start = Gtk.Button(label="Start")
        self.button_start.connect("clicked", self.start_unarchiving)
        vbox.pack_start(self.button_start, True, True, 0)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_fraction(0)
        self.progress_bar.set_text("0%")
        self.progress_bar.set_show_text(True)
        vbox.pack_start(self.progress_bar, True, True, 0)
        
        # Status label
        self.status_label = Gtk.Label(label="Status: Waiting to start")
        self.status_label.set_xalign(0)
        vbox.pack_start(self.status_label, True, True, 0)

        self.worker = None
        
    def choose_dest_folder(self, widget, label):
        # Choosing destination folder
        dialog = Gtk.FileChooserDialog(
            title="Choose destination folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Choose", Gtk.ResponseType.OK
        )
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            label.set_text(f"Destination folder: {dialog.get_filename()}")
            
        dialog.destroy()

    def start_unarchiving(self, widget):
        # Unachiving process: get all params
        delete_files = self.check_delete_files.get_active()
        password = self.entry_password.get_text()
        
        # Check destination folder
        destination = self.folder_label.get_text().replace("Destination folder: ", "")
        if not destination or destination == "None selected":
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="Error",
            )
            dialog.format_secondary_text("Destination folder not selected.")
            dialog.run()
            dialog.destroy()
            return

        # Run worker
        self.button_start.set_sensitive(False)
        self.status_label.set_text("Status: Processing...")
        self.worker = WorkerGtk(
            mode='unarchive',
            files=self.selected_files,
            destination=destination,
            password=password,
            archive_name=None,
            delete_files=delete_files,
            format=None,
            compression_level=None
        )
        self.worker.connect("progress", self.on_progress)
        self.worker.connect("error", self.show_error)
        self.worker.connect("finished", self.task_completed)
        self.worker.start()

    def on_progress(self, worker, value):
        self.progress_bar.set_fraction(value / 100)
        self.progress_bar.set_text(f"{value}%")

    def show_error(self, worker, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
        self.progress_bar.set_fraction(0)
        self.status_label.set_text("Status: Error")
        self.button_start.set_sensitive(True)

    def task_completed(self, worker):
        if int(self.progress_bar.get_fraction() * 100) == 100:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Completed",
            )
            dialog.format_secondary_text("Operation completed successfully.")
            dialog.run()
            dialog.destroy()

        self.progress_bar.set_fraction(0)
        self.status_label.set_text("Status: Waiting to start")
        self.button_start.set_sensitive(True)
