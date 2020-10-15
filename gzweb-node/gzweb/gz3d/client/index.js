$(document).ready(function () {
    var editors = {};
    var apiUrls = {};

    $.ajax({
        url: '/get-api-urls',
        success: function (data) {
            apiUrls = data;
        },
        async: false
    });

    document.getElementById('a-export-project').setAttribute('href', apiUrls.exportProject);

    function newEditor(taId) {
        return CodeMirror.fromTextArea(document.getElementById(taId), {
            mode: "python",
            lineNumbers: false,
            styleActiveLine: true,
            matchBrackets: true,
            autoCloseBrackets: true
        });
    }

    function getActiveTab() {
        var children = $('#tab-list').children('li.active');
        if (children.length == 0) {
            return null;
        }
        return $(children[0]);
    }

    function getActiveEditor() {
        var tab = getActiveTab();
        if (tab == null) {
            return null;
        }
        var id = tab.attr('id').replace('li-', 'editor-');
        return editors[id];
    }

    function showChangedIcon(show) {
        var tab = getActiveTab();
        if (tab == null) {
            return;
        }
        var changedIconId = tab.attr('id').replace('li-', 'change-');
        $('#' + changedIconId).prop('hidden', !show);
    }

    function getActiveFilePath() {
        var tab = getActiveTab();
        if (tab == null) {
            return null
        }
        var filePath = tab.attr('data-filepath');
        return filePath;
    }

    function refreshTree() {
        $('#tree').jstree(true).refresh();
    }

    function addFile() {
        var fileName = prompt('Enter file name');
        $.post(apiUrls.addFile, {
            'file_name': fileName
        }, function () {
            refreshTree();
        });
    }


    function addFolder() {
        var folderName = prompt('Enter folder name');
        $.post(apiUrls.addFolder, {
            'name': folderName
        }, function () {
            refreshTree();
        });
    }


    $(document).on('click', '#a-add-file', function () {
        addFile();
    });


    $(document).on('click', '#a-add-folder', function () {
        addFolder();
    });


    $(document).on('click', '#btn-run', function () {
        var editor = getActiveEditor();
        if (editor == null) {
            return;
        }
        $.post(apiUrls.runCode, {
            code: editor.getValue()
        }, function (data) {
            $('#output').html(data.result);
        });
    });

    $(document).on('click', '#btn-save', function () {
        var editor = getActiveEditor();
        var filePath = getActiveFilePath();
        if (editor == null || filePath == null) {
            return;
        }
        $.post(apiUrls.saveFile, {
            file_name: filePath,
            code: editor.getValue()
        }, function () {
            showChangedIcon(false);
            var editor = getActiveEditor();
            editor.initialHash = md5(editor.getValue());
        });
    });

    $('#tree').jstree({
        'core': {
            'data': {
                'url': apiUrls.getFileTree
            }
        },
        'plugins': ['contextmenu', 'search', 'sort', 'types'],
        'contextmenu': {
            'select_node': false,
            'items': function (node) {
                var menus = {}
                if (node.type == 'file') {
                    menus['runFile'] = {
                        'label': 'Run file',
                        'action': function () {
                            $.post(apiUrls.runFile, {
                                'file_name': node.data.path
                            }, function (data) {
                                $('#output').html(data.result);
                            });
                        }
                    }

                    menus['removeFile'] = {
                        'separator_before': true,
                        'label': 'Remove file',
                        'action': function () {
                            $.post(apiUrls.removeFile, {
                                'file_name': node.data.path
                            }, function () {
                                refreshTree();
                            });
                        }
                    }
                } else if (node.type == 'folder') {
                    menus['addFile'] = {
                        'label': 'Add file',
                        'action': addFile
                    }
                    menus['addFolder'] = {
                        'label': 'Add folder',
                        'action': addFolder
                    }
                    menus['removeFolder'] = {
                        'label': 'Remove folder',
                        'action': function () {
                            $.post(apiUrls.removeFolder, {
                                'name': node.data.path
                            }, function () {
                                refreshTree();
                            });
                        }
                    }
                }
                return menus;
            }
        },
        'search': {
            'show_only_matches': true
        },
        'sort': function (node1, node2) {
            if (this.get_type(node1) != this.get_type(node2)) {
                return this.get_type(node1) == 'folder' ? -1 : 1;
            } else {
                return this.get_text(node1) > this.get_text(node2) ? 1 : -1;
            }
        },
        'types': {
            'file': {
                'icon': '/static/pyfile.png'
            },
            'folder': {}
        }
    });

    $('#tree').on('select_node.jstree', function (e, data) {
        if (data.node.type != 'file') {
            return;
        }
        var liId = `li-${data.node.id}`;
        var tabId = `tab-${data.node.id}`;
        var editorId = `editor-${data.node.id}`;
        var closeId = `close-${data.node.id}`;
        var changedId = `change-${data.node.id}`;

        if ($('#tab-list').children(`#${liId}`).length == 0) {
            $('#tab-list').append(
                `<li id="${liId}" data-filepath="${data.node.data.path}">
            <a href="#${tabId}" data-toggle="tab">${data.node.text}
              <span hidden class="file-changed" id="${changedId}">*&nbsp;</span>
              <span class="close-tab" id="${closeId}">&nbsp;x</span></a></li>`
            );

            $('#tab-content').append(
                `<div id="${tabId}" class="tab-pane"><textarea id="${editorId}"></textarea></div>`);

            editors[editorId] = newEditor(editorId);

            $('#tab-list a:last').tab('show');
            $.get(apiUrls.getFileContent + '?file=' + data.node.data.path, {}, function (data) {
                editors[editorId].setValue(data.code);
                editors[editorId].initialHash = md5(editors[editorId].getValue());
                editors[editorId].on('change', function (editor) {
                    hash = md5(editor.getValue());
                    showChangedIcon(hash != editor.initialHash);
                });
            });
        } else {
            $(`#tab-list a[href="#${tabId}"]`).tab('show');
        }
    });

    $(document).on('click', '#btn-upload', function () {
        var formData = new FormData();
        formData.append('file', document.getElementById('file-upload').files[0]);
        $.ajax({
            url: apiUrls.importProject,
            data: formData,
            type: 'POST',
            contentType: false,
            processData: false,
            success: function () {
                refreshTree();
                document.getElementById('file-upload').value = '';
            }
        });
    });

    $(document).on('click', '.close-tab', function (ev) {
        var id = $(ev.target).attr('id');
        var liId = id.replace('close-', 'li-');
        var tabId = id.replace('close-', 'tab-');
        var editorId = id.replace('close-', 'editor-');
        $('#' + liId).remove();
        $('#' + tabId).remove();
        delete editors[editorId];
        $('#tab-list a:first').tab('show');
    });

    var to = false;
    $('#tree-q').keyup(function () {
        if (to) {
            clearTimeout(to);
        }
        to = setTimeout(function () {
            var v = $('#tree-q').val();
            $('#tree').jstree(true).search(v);
        }, 250);
    });
});