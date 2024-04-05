// 当用户点击窗口外时关闭弹出窗口
window.onclick = function(event) {
  var popupContainer = document.getElementById('popup-container');
  if (event.target == popupContainer) {
    popupContainer.style.display = 'none';
  }
}

function closePopup() {
  document.getElementById('popup-container').style.display = 'none';
}

// Function to open the popup
function openPopup() {
  document.getElementById('popup-container').style.display = 'flex';
}

function setTitle(title) {
  document.getElementById('header-title').innerText = title + '-要素提取';
}

function updateExtractor(selectElement) {
  var uuid = selectElement.value; // 获取选中的value
  var text = selectElement.options[selectElement.selectedIndex].text; // 获取选中的option的文本

  fetch('/extractor/selected', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({"uuid": uuid }),
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    setTitle(text);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}

function getExtractor() {
  // 使用 fetch 发送 GET 请求到 /extractor
  fetch('/extractor')
    .then(response => response.json()) // 解析 JSON 返回的数据
    .then(data => {
      const selectElement = document.getElementById('extractor-options');
      // 清除 select 元素的现有 options
      selectElement.innerHTML = '';
      // 使用返回的数据创建新的 option 元素
      data.data.forEach(item => {
        const option = new Option(item.name, item.uuid);
        if (item.selected === true || item.selected > 0) {
          option.selected = true;
          setTitle(item.name);
        }
        selectElement.add(option);
      });
    })
    .catch(error => {
      console.error('Error fetching data: ', error);
    });
}
// 当文档加载完成时，执行此函数
document.addEventListener('DOMContentLoaded', getExtractor);