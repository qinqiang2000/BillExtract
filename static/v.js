// 存储当前上传的文件名
var currentFilename = '';
// 存储选择的文件和处理状态的数组
var filesToUpload = [];

var isDragging = false;
var leftPanel = document.getElementById('pdf-viewer');
var rightPanel = document.getElementById('json-viewer');
var gutter = document.getElementById('gutter');
var container = document.getElementById('container');

function addFiles(newFiles) {
  filesToUpload = []
  for (var i = 0; i < newFiles.length; i++) {
    filesToUpload.push({ file: newFiles[i], processed: 0 });
  }
}

function containsKeyword(value, keywords) {
  if (typeof value !== 'string') {
    return false;
  }
  // 使用Array.prototype.some检查是否至少有一个关键字包含在value中
  return keywords.some(keyword => value.includes(keyword));
}

// 获取当前时间的函数
function getCurrentTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = now.getSeconds().toString().padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
}

// 打印带有时间戳的日志
function log(...args) {
  const timestamp = getCurrentTime();
  console.log(`[${timestamp}]`, ...args);
}

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('single-upload-btn').focus();
  var hostname = window.location.hostname;
  var port = window.location.port;

  var socket = io.connect('http://' + hostname + ':' + port);

  socket.on('connect', function () {
    console.log('WebSocket connected!');
    socket.emit('start_data_transfer');  // 告知服务器开始数据传输
  });

  // 进度处理
  socket.on('progress', function (data) {
    log('Progress: ' + JSON.stringify(data));

    if (data.progress)
      document.getElementById('progressBar').style.width = data.progress + '%';

    if (data.status)
      document.getElementById('progress-status').textContent = data.status;

    // 当data.status包含‘done’时，隐藏进度条
    if (data.status.includes('done')) {
      log('Progress: done');
      document.getElementById('progress-container-wrapper').style.display = 'none';
      document.getElementById('progress-status').style.display = 'none';
      document.getElementById('second-upload-form').style.display = 'flex';
      // document.getElementById('json-code').style.display = 'none';

      // 滚动到顶部
      rightPanel.scrollTop = 0;
    }
  });

  socket.on('data', function (data) {
    if (!data.data) return

    document.getElementById('table-container').style.display = 'block';

    createTableList(data.data, data.page)
  });

  // 流试数据处理
  socket.on('stream_chunk', function (data) {
    if (!data.text) return
    document.getElementById('json-code').style.display = 'block';
    document.getElementById('json-code').innerHTML = `<code class="json">${data.text}</code>`;
    hljs.highlightBlock(document.querySelector('#json-code code'));
    rightPanel.scrollTop = rightPanel.scrollHeight;
  });

  //  创建一个表格
  function createTable(data) {
    var table = document.createElement('table');
    table.classList.add('data-table'); // 添加样式类

    // 遍历 JSON 对象
    for (var key in data) {
      if (data.hasOwnProperty(key)) {
        var value = data[key];

        // 如果value是一个对象，则转成字符串
        if (typeof value === 'object') {
          value = JSON.stringify(value);
        }

        // 如果value为空，则设置为占位符
        const keywords = ["null", "undefined", "不明确"];
        if (value == null || value == undefined || value == '' || containsKeyword(value, keywords)) {
          value = 'N/A';
        }

        // 创建表格行
        var row = table.insertRow(-1);
        var cellKey = row.insertCell(0);
        var cellValue = row.insertCell(1);
        var cellIcon = row.insertCell(2); // 新增图标列

        cellKey.innerHTML = key;

        cellValue.innerHTML = value;
        cellValue.setAttribute('contenteditable', false);
        cellValue.addEventListener('keydown', function (event) {
          if (event.key === 'Enter' && !event.shiftKey) {
            var newValue = this.innerText; // 获取新的值
            var iconElement = this.nextElementSibling.querySelector('svg'); // 获取下一个单元格的svg元素
            log('单元格内容已更新', iconElement)
            // 发送数据到后端
            sendIconClickDataToBackend(iconElement, newValue);
            this.contentEditable = false;
          }
          else if (event.key === 'Escape') {
            this.contentEditable = false;
            this.innerText = this.getAttribute('oldValue'); // 恢复旧值
          }
        });
        cellValue.addEventListener('paste', function (event) {
          event.preventDefault(); // 阻止默认粘贴行为,避免把格式也粘贴了
          var text = '';
          // 获取剪贴板中的文本
          if (event.clipboardData || event.originalEvent.clipboardData) {
            text = (event.clipboardData || event.originalEvent.clipboardData).getData('text/plain');
          } else if (window.clipboardData) {
            text = window.clipboardData.getData('Text');
          }
          // 将纯文本插入到单元格中
          document.execCommand('insertText', false, text);
        });

        // 添加 thumb-down 图标
        cellIcon.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-md"><path fill-rule="evenodd" clip-rule="evenodd" d="M11.8727 21.4961C11.6725 21.8466 11.2811 22.0423 10.8805 21.9922L10.4267 21.9355C7.95958 21.6271 6.36855 19.1665 7.09975 16.7901L7.65054 15H6.93226C4.29476 15 2.37923 12.4921 3.0732 9.94753L4.43684 4.94753C4.91145 3.20728 6.49209 2 8.29589 2H18.0045C19.6614 2 21.0045 3.34315 21.0045 5V12C21.0045 13.6569 19.6614 15 18.0045 15H16.0045C15.745 15 15.5054 15.1391 15.3766 15.3644L11.8727 21.4961ZM14.0045 4H8.29589C7.39399 4 6.60367 4.60364 6.36637 5.47376L5.00273 10.4738C4.65574 11.746 5.61351 13 6.93226 13H9.00451C9.32185 13 9.62036 13.1506 9.8089 13.4059C9.99743 13.6612 10.0536 13.9908 9.96028 14.2941L9.01131 17.3782C8.6661 18.5002 9.35608 19.6596 10.4726 19.9153L13.6401 14.3721C13.9523 13.8258 14.4376 13.4141 15.0045 13.1902V5C15.0045 4.44772 14.5568 4 14.0045 4ZM17.0045 13V5C17.0045 4.64937 16.9444 4.31278 16.8338 4H18.0045C18.5568 4 19.0045 4.44772 19.0045 5V12C19.0045 12.5523 18.5568 13 18.0045 13H17.0045Z" fill="currentColor"></path></svg>';
        var svgElement = cellIcon.querySelector('svg');
        //        svgElement.setAttribute('page', page);
        svgElement.setAttribute('key', key);
        svgElement.addEventListener('click', function () {
          var editableCell = this.parentNode.previousElementSibling; // 假设编辑按钮位于单元格旁边
          var oldValue = editableCell.innerText;
          editableCell.setAttribute('oldValue', oldValue); // 保存旧值
          editableCell.contentEditable = true;
          editableCell.focus(); // 焦点放在单元格上，以便开始编辑
        });
      }
    }
    return table;
  }

  // 创建表格
  function createTableList(data, page) {
    var container = document.getElementById('table-container');

    // 创建表格标题
    const title = document.createElement('h3');
    title.textContent = `第 ${page} 页`;
    title.setAttribute('page', page);
    title.addEventListener('click', function () {
      getPageText(this);
    });

    container.appendChild(title);

    // 创建表格，并添加到容器
    for (var i = 0; i < data.length; i++) {
      var table = createTable(data[i]);
      container.appendChild(table);
    }
  }

  // 发送点击图标的数据到后台 
  function sendIconClickDataToBackend(iconElement, newValue) {
    // isClicked=0 表示未点击, 发送到后台已点击状态，并修改图标为已点击颜色;反之亦然
    isClicked = iconElement.classList.contains('icon-clicked')
    var page = iconElement.getAttribute('page');
    var key = iconElement.getAttribute('key');

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/down', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({ page: page, key: key, clicked: !isClicked, filename: currentFilename, value: newValue }));
    log('发送点击图标的数据到后台', { page: page, key: key, clicked: !isClicked, filename: currentFilename });

    xhr.onload = function () {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        if (response.status === 'success') {
          console.log('Down data sent to backend successfully');
          iconElement.classList.toggle('icon-clicked');
        } else {
          alert(response.msg);
        }
      } else {
        alert('无法发送data到后台');
      }
    };
  }

  // 获取后端返回的中间文本
  function getPageText(titleElement) {
    page = titleElement.getAttribute('page');
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/text', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({ page: page, filename: currentFilename }));
    xhr.onload = function () {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        if (response.status === 'success') {
          var newWindow = window.open('', '_blank');
          newWindow.document.write('<html><head><title>数据展示</title><style>p { white-space: pre-wrap; }</style></head><body>');
          newWindow.document.write('<p>' + response.text + '</p>'); // 假设 responseData 是您通过 AJAX 获取的数据
          newWindow.document.write('</body></html>');
          newWindow.document.close();
        } else {
          alert(response.msg);
        }
      } else {
        alert('无法发送data到后台');
      }
    };
  }

  function upload_one_file(file) {
    var formData = new FormData();
    formData.append('file', file);
    log('开始上传文件', file);

    document.getElementById('second-upload-form').style.display = 'none';

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);
    xhr.onload = function () {
      if (xhr.status === 200) {
        console.log(xhr.responseText)

        var response = JSON.parse(xhr.responseText);
        var uploadedFileName = response.filename;
        currentFilename = uploadedFileName;
        log('文件上传成功', uploadedFileName);
        
        // 清空表格
        table = document.getElementById("table-container");
        table.innerHTML = ""
        document.getElementById('progress-container-wrapper').style.display = 'block';
        document.getElementById('progress-status').style.display = 'block';

        // 清空日志
        document.getElementById('json-code').innerHTML = ''

        var pdfViewer = document.getElementById('pdf-viewer');

        // 判断uploadedFileName是否是pdf文件
        if (uploadedFileName.endsWith('.pdf')) {
          // 更新 embed 标签的 src 属性
          var embedTag = '<embed src="/uploaded?filepath=' + encodeURIComponent(uploadedFileName) + '" type="application/pdf" width="100%" height="100%" />';
        } 
        else {
          var embedTag = `
          <div class="image-container">
              <img id="preview-image" src="/uploaded?filepath=`+ encodeURIComponent(uploadedFileName)  +`" alt="预览图片">
          </div>
          <div class="btn-img" style="text-align: center; margin-top: 30px;">
              <button onclick="zoomIn()" aria-label="放大" style="border: none; background-color: transparent; cursor: pointer;">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-zoom-in">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  <line x1="11" y1="8" x2="11" y2="14"></line>
                  <line x1="8" y1="11" x2="14" y2="11"></line>
              </svg></button>
              <button onclick="zoomOut()" aria-label="缩小" style="border: none; background-color: transparent; cursor: pointer;">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-zoom-out">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  <line x1="8" y1="11" x2="14" y2="11"></line>
              </svg></button>
              <button onclick="rotate()" aria-label="旋转" style="border: none; background-color: transparent; cursor: pointer;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-rotate-cw">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <path d="M20.49 15C19.35 18.65 15.95 21 12 21c-4.42 0-8-3.58-8-8s3.58-8 8-8c1.66 0 3.2 0.51 4.45 1.38"></path>
                </svg>
              </button>
          </div>
          `
        }
        pdfViewer.innerHTML = embedTag;

        document.getElementById('json-viewer').style.display = 'block';

        // 更新为已处理状态
        filesToUpload.find(f => f.file === file).processed = 1;
        var totalFiles = filesToUpload.length;
        var processedFiles = filesToUpload.filter(f => f.processed === 1).length;
        document.getElementById('next-upload-btn').textContent = `下一文件(${processedFiles}/${totalFiles})`;
        log('filesToUpload', filesToUpload);
      } else {
        log('文件上传失败');
      }
    };

    xhr.send(formData);
  }

  function upload_files(elem) {
    const files = Array.from(elem.files);
    const allowedExtensions = ['pdf', 'jpg', 'jpeg', 'png'];
    const filteredFiles = files.filter(file => {
      const fileExtension = file.name.split('.').pop().toLowerCase();
      return allowedExtensions.includes(fileExtension);
    });
    if (filteredFiles.length < 1) {
      alert("请选择pdf, jpg, jpeg或png文件");
      return
    }

    addFiles(filteredFiles);
    upload_one_file(filteredFiles[0]);
  }

  gutter.addEventListener('mousedown', function (e) {
    e.preventDefault();
    isDragging = true;
  });

  document.addEventListener('mousemove', function (e) {
    // Only resize if dragging is active
    if (!isDragging) return;

    var containerRect = container.getBoundingClientRect();
    var leftWidth = e.clientX - containerRect.left;
    var rightWidth = containerRect.right - e.clientX;

    leftPanel.style.width = `${leftWidth}px`;
    rightPanel.style.flexGrow = 1; // 防止右侧面板伸展
  });

  document.addEventListener('mouseup', function (e) {
    isDragging = false;
  });

  document.getElementById('file-upload').addEventListener('change', function () {
    upload_files(this)
  });

  document.getElementById('single-file-upload').addEventListener('change', function () {
    upload_files(this)
  });

  document.getElementById('second-file-upload').addEventListener('change', function () {
    upload_files(this)
  });

  document.getElementById('upload-btn').addEventListener('click', function () {
    document.getElementById('file-upload').click();
  });

  document.getElementById('single-upload-btn').addEventListener('click', function () {
    document.getElementById('single-file-upload').click();
  });

  document.getElementById('second-upload-btn').addEventListener('click', function () {
    document.getElementById('second-file-upload').click();
  });

  document.getElementById('export-btn').addEventListener('click', function () {
    // 读取所有的表格
    const tables = document.querySelectorAll('.data-table');
    const allTablesData = [];

    // 遍历每个表格
    tables.forEach(table => {
      const rows = table.querySelectorAll('tr');
      const tableData = {};
      // 遍历每一行
      rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 2) {
          // 使用第一列的内容作为键，第二列的内容作为值
          const key = cells[0]?.innerText.trim();
          const value = cells[1]?.innerText.trim();
          if (key && value) { // 确保键和值都存在
            tableData[key] = value;
          }
        }
      });
      allTablesData.push(tableData);
    });

    log('导出数据', allTablesData);

    // 创建一个 Blob 对象，类型为 JSON
    const dataStr = JSON.stringify(allTablesData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });

    // 创建一个下载链接
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'tables-data.json';

    // 触发下载
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

  });

  document.getElementById('next-upload-btn').addEventListener('click', function () {
    var nextFile = filesToUpload.find(f => f.processed === 0);
    if (nextFile)
      upload_one_file(nextFile.file);
    else {
      document.getElementById('second-upload-btn').style.display = 'flex';
      alert('本次没有更多文件');
    }
  });
});

