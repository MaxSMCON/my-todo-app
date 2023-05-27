import zipfile

def extractor_archive(archive_path, dest_dir):
    with zipfile.ZipFile(archive_path, 'r') as archive:
        archive.extractall(dest_dir)

if __name__ == '__main__':
    extractor_archive("compressed.zip",
                      "\msmetanin\OneDrive - Conestoga Meat Packers Ltd\Documents\Courses\Python\PythonMega/bonus")


