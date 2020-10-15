import os
import shutil
import subprocess
from urllib.parse import parse_qs, urlsplit

from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from stringcase import camelcase

from code_editor.settings import EDITOR_DIR, ROS_DIR, ROS_FILE, LAUNCH_CMD
from . import utils
from .apps import ApiConfig
from .forms import UploadFileForm
from .utils import status500_if_exception


@status500_if_exception
def get_urls(request):
    host = request.get_raw_uri().replace(request.get_full_path(), '')
    funcs = utils.get_module_functions(__name__)
    urls = {}
    for func in funcs:
        url = host + reverse(f'{ApiConfig.name}:{func.__name__}')
        urls[camelcase(func.__name__)] = url
    return JsonResponse(urls, safe=False)


@status500_if_exception
def get_file_tree(request):
    items = [utils.tree_root()]
    for root, dirs, files in os.walk(EDITOR_DIR):
        parent = root[len(EDITOR_DIR)+1:]
        items += [utils.tree_file(f, parent) for f in files if f.endswith('.py')]
        items += [utils.tree_folder(d, parent) for d in dirs]
    return JsonResponse(items, safe=False)


@status500_if_exception
def get_file_content(request):
    url = request.get_raw_uri()
    file_name = parse_qs(urlsplit(url).query)['file'][0]
    full_path = os.path.join(EDITOR_DIR, file_name)
    with open(full_path, 'r', encoding='utf8') as f:
        code = f.read()
    return JsonResponse({'code': code}, safe=False)


@status500_if_exception
def save_file(request):
    file_path = os.path.join(EDITOR_DIR, request.POST.get('file_name'))
    code = request.POST.get('code')
    with open(file_path, 'w', encoding='utf') as f:
        f.write(code)
    return HttpResponse(status=200)


@status500_if_exception
def run_code(request, code=None):
    code = code or request.POST.get('code')
    if os.path.exists(ROS_DIR):
        shutil.rmtree(ROS_DIR)
    shutil.copytree(EDITOR_DIR, ROS_DIR)
    with open(ROS_FILE, 'w', encoding='utf8') as f:
        f.write(code)
    p = subprocess.Popen(LAUNCH_CMD, stdout=subprocess.PIPE)
    out = p.stdout.read()
    return JsonResponse({'result': out.decode('utf8')}, safe=False)


@status500_if_exception
def run_file(request):
    file_name = request.POST.get('file_name')
    file_path = os.path.join(EDITOR_DIR, file_name)
    with open(file_path, 'r', encoding='utf8') as f:
        code = f.read()
    return run_code(request, code)


@status500_if_exception
def add_file(request):
    file_name = (request.POST.get('file_name') or 'new') + '.py'
    file_path = os.path.join(EDITOR_DIR, file_name)
    open(file_path, 'w', encoding='utf8').close()
    return HttpResponse(status=200)


@status500_if_exception
def remove_file(request):
    file_name = request.POST.get('file_name')
    file_path = os.path.join(EDITOR_DIR, file_name)
    os.remove(file_path)
    return HttpResponse(status=200)


@status500_if_exception
def add_folder(request):
    name = request.POST.get('name')
    full_path = os.path.join(EDITOR_DIR, name)
    os.makedirs(full_path)
    return HttpResponse(status=200)


@status500_if_exception
def remove_folder(request):
    name = request.POST.get('name')
    full_path = os.path.join(EDITOR_DIR, name)
    shutil.rmtree(full_path)
    return HttpResponse(status=200)


@status500_if_exception
def  export_project(request):
    content = utils.zip_dir(EDITOR_DIR)
    return HttpResponse(content, content_type='application/zip')


@status500_if_exception
def import_project(request):
    form = UploadFileForm(request.POST, request.FILES)
    if not form.is_valid():
        raise Exception('wrong post result')
    utils.handle_uploaded_file(request.FILES['file'])    
    return HttpResponse(status=200)
