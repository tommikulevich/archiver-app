import os
import py7zr
import zipfile
import tarfile
import threading
from gi.repository import GObject
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


class WorkerGtk(GObject.GObject, threading.Thread):
    __gsignals__ = {
        'progress': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        'error': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'finished': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, mode, files, destination, password, archive_name, delete_files, format, compression_level):
        GObject.GObject.__init__(self)
        threading.Thread.__init__(self)
        self.mode = mode
        self.files = files
        self.destination = destination
        self.password = password
        self.archive_name = archive_name
        self.delete_files = delete_files
        self.format = format
        self.compression_level = compression_level
        
        print(f"Mode: '{mode}' | Compression level: '{compression_level}' | Format: '{format}' | Password: '{password}'")

    def run(self):
        try:
            if self.mode == 'archive':
                self.archive_files()
            elif self.mode == 'unarchive':
                self.unarchive_files()
            GObject.idle_add(self.emit, 'finished')
        except Exception as e:
            GObject.idle_add(self.emit, 'error', str(e))
            return
       
    def count_files(self, files):
        count = 0
        for file in files:
            if os.path.isdir(file):
                for _, _, filenames in os.walk(file):
                    count += len(filenames)
            else:
                count += 1
        return count

    def archive_files(self):
        archive_path = os.path.join(self.destination, self.archive_name + self.format)
        total_files = self.count_files(self.files)
        processed_files = 0

        try:
            if self.format == '.zip':
                with zipfile.ZipFile(archive_path, 'w', compression=self.compression_level_zip(self.compression_level)) as archive:
                    for file in self.files:
                        if os.path.isdir(file):
                            for root, _, files in os.walk(file):
                                for filename in files:
                                    file_path = os.path.join(root, filename)
                                    archive.write(file_path, os.path.relpath(file_path, self.files[0]))
                                    processed_files += 1
                                    GObject.idle_add(self.emit, 'progress', int(100 * processed_files / total_files))
                        else:
                            archive.write(file, os.path.basename(file))
                            processed_files += 1
                            GObject.idle_add(self.emit, 'progress', int(100 * processed_files / total_files))
            elif self.format == '.7z':
                with py7zr.SevenZipFile(archive_path, 'w', filters=self.sevenzip_filters(self.compression_level)) as archive:
                    for file in self.files:
                        if os.path.isdir(file):
                            for root, _, files in os.walk(file):
                                for filename in files:
                                    file_path = os.path.join(root, filename)
                                    archive.write(file_path, os.path.relpath(file_path, self.files[0]))
                                    processed_files += 1
                                    GObject.idle_add(self.emit, 'progress', int(100 * processed_files / total_files))
                        else:
                            archive.writeall(file)
                            processed_files += 1
                            GObject.idle_add(self.emit, 'progress', int(100 * processed_files / total_files))
            elif self.format == '.tar':
                with tarfile.open(archive_path, f'w:{self.tar_compression()}') as archive:
                    for file in self.files:
                        if os.path.isdir(file):
                            for root, _, files in os.walk(file):
                                for filename in files:
                                    file_path = os.path.join(root, filename)
                                    archive.add(file_path, arcname=os.path.relpath(file_path, self.files[0]))
                                    processed_files += 1
                                    GObject.idle_add(self.emit, 'progress', int(100 * processed_files / total_files))
                        else:
                            archive.add(file, os.path.basename(file))
                            processed_files += 1
                            GObject.idle_add(self.emit, 'progress', int(100 * processed_files / total_files))
                        
            if self.delete_files:
                for file in self.files:
                    if os.path.isfile(file):
                        os.remove(file)
                    elif os.path.isdir(file):
                        for root, _, files in os.walk(file):
                            for filename in files:
                                os.remove(os.path.join(root, filename))
                        os.rmdir(file)

            if self.password:
                self.encrypt_file(archive_path)
        except Exception as e:
            GObject.idle_add(self.emit, 'error', str(e))

    def unarchive_files(self):
        try:
            for archive in self.files:
                if self.is_encrypted(archive):
                    if not self.password:
                        GObject.idle_add(self.emit, 'error', "Plik jest zaszyfrowany. Brak podanego hasła.")
                        return
                    decrypted_path = self.decrypt_file(archive)
                else:
                    decrypted_path = archive
                    
                if archive.endswith('.zip'):
                    with zipfile.ZipFile(decrypted_path, 'r') as archive_file:
                        total_files = len(archive_file.namelist())
                        for i, file in enumerate(archive_file.namelist(), 1):
                            archive_file.extract(file, self.destination)
                            GObject.idle_add(self.emit, 'progress', int(100 * i / total_files))
                elif archive.endswith('.7z'):
                    with py7zr.SevenZipFile(decrypted_path, mode='r') as archive_file:
                        archive_content = archive_file.getnames()
                        total_files = len(archive_content)
                        for i, file in enumerate(archive_content, 1):
                            archive_file.reset()
                            archive_file.extract(targets=[file], path=self.destination)
                            GObject.idle_add(self.emit, 'progress', int(100 * i / total_files))
                elif archive.endswith(('.tar', '.tar.gz', '.tar.bz2', '.tar.xz')):
                    with tarfile.open(decrypted_path, 'r:*') as archive_file:
                        members = archive_file.getmembers()
                        total_files = len(members)
                        for i, file in enumerate(members, 1):
                            archive_file.extract(file, self.destination)
                            GObject.idle_add(self.emit, 'progress', int(100 * i / total_files))

                if decrypted_path != archive:
                    os.remove(decrypted_path)
                    
                GObject.idle_add(self.emit, 'progress', int(100 * (self.files.index(archive) + 1) / len(self.files)))

                if self.delete_files:
                    os.remove(archive)
        except Exception as e:
            GObject.idle_add(self.emit, 'error', str(e))

    def is_encrypted(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                header = file.read(9)
            return header == b'ENCRYPTED'
        except Exception:
            return False

    def encrypt_file(self, filepath):
        salt = os.urandom(16)
        key = self.derive_key(self.password, salt)
        aesgcm = AESGCM(key)
        with open(filepath, 'rb') as file:
            data = file.read()
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, data, None)
        with open(filepath, 'wb') as file:
            file.write(b'ENCRYPTED' + salt + nonce + ct)

    def decrypt_file(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                header = file.read(9)
                if header != b'ENCRYPTED':
                    raise ValueError("Niepoprawny nagłówek pliku szyfrowania.")
                salt = file.read(16)
                nonce = file.read(12)
                ct = file.read()
            key = self.derive_key(self.password, salt)
            aesgcm = AESGCM(key)
            data = aesgcm.decrypt(nonce, ct, None)
            decrypted_path = filepath + '.dec'
            with open(decrypted_path, 'wb') as file:
                file.write(data)
            return decrypted_path
        except InvalidTag:
            raise ValueError("Niepoprawne hasło lub uszkodzone dane.")
    
    def compression_level_zip(self, level):
        if level == 'Szybki':
            return zipfile.ZIP_DEFLATED
        elif level == 'Maksymalny':
            return zipfile.ZIP_BZIP2
        
        return zipfile.ZIP_STORED

    def sevenzip_filters(self, level):
        if level == 'Maksymalny':
            return [{'id': py7zr.FILTER_LZMA2, 'preset': 9}]
        elif level == 'Normalny':
            return [{'id': py7zr.FILTER_LZMA2, 'preset': 5}]
        
        return [{'id': py7zr.FILTER_LZMA2, 'preset': 1}]
    
    def tar_compression(self):
        if self.compression_level == 'Szybki':
            return 'gz'
        elif self.compression_level == 'Maksymalny':
            return 'bz2'
        
        return ''

    def derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

GObject.type_register(WorkerGtk)