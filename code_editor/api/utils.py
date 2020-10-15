from functools import wraps
from hashlib import md5
import os
import shutil
import sys
import tempfile
import types
import zipfile

from django.http import JsonResponse

from code_editor.settings import EDITOR_DIR


def node_id(s):
    return md5(s.encode('utf8')).hexdigest()


ROOT_NODE_PATH = '.'
ROOT_NODE_ID = node_id(ROOT_NODE_PATH)


def status500_if_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, safe=False, status=500)

    return wrapper


def tree_root():
    return {
        'id': ROOT_NODE_ID, 
        'parent': '#', 
        'text': 'Project', 
        'type': 'folder', 
        'state': {'opened': True}, 
        'data': {'path': ROOT_NODE_PATH}
    }


def tree_file(file_name, parent=None):
    path = os.path.join(parent, file_name)
    item = {
        'id': node_id(path),
        'parent': parent or ROOT_NODE_ID,
        'text': file_name,
        'data': {'path': path },
        'type': 'file'
    }
    return item


def tree_folder(name, parent=None):
    path =  os.path.join(parent, name)
    item = {
        'id': path,
        'parent': parent or ROOT_NODE_ID,
        'text': name,
        'type': 'folder',
        'data': {
            'path': path
        }
    }
    return item


def zip_dir(dir_path):
    zip_path = os.path.join(tempfile.mkdtemp(), 'project.zip')
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if not f.endswith('.py'):
                continue
            absname = os.path.join(root, f)
            arcname = absname[len(dir_path) + 1:]
            zipf.write(absname, arcname)
    zipf.close()
    with open(zip_path, 'rb') as f:
        content = f.read()
    os.remove(zip_path)
    return content


def unzip(zip_path, unzip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip:
        zip.extractall(unzip_path)


def handle_uploaded_file(f):
    full_path = os.path.join(tempfile.mkdtemp(), 'project.zip')
    with open(full_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    shutil.rmtree(EDITOR_DIR)
    os.mkdir(EDITOR_DIR)
    unzip(full_path, EDITOR_DIR)



def get_module_functions(module_name):
    module = sys.modules[module_name]
    funcs = []
    for item in dir(module):
        attr = getattr(module, item)
        if not (isinstance(attr, types.FunctionType) and attr.__module__ == module_name):
            continue
        funcs.append(attr)
    return funcs