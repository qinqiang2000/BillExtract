// Global variable to store the extractors data
var extractorsData = [];
var defaultExtractorHtml = `
<h1 id="extractor-name" contenteditable="true" data-placeholder="输入新提取器的名字..."></h1>
<p>提示词：</p>
<textarea class="prompt-text" id="prompt-text" placeholder="请输入需提取的要素和说明, 不少于30字"></textarea>
<button type="button" id="create-button" class="create-button" disabled>保存</button>
`;
var delSvg = '<span class="link-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-md"><path fill-rule="evenodd" clip-rule="evenodd" d="M10.5555 4C10.099 4 9.70052 4.30906 9.58693 4.75114L9.29382 5.8919H14.715L14.4219 4.75114C14.3083 4.30906 13.9098 4 13.4533 4H10.5555ZM16.7799 5.8919L16.3589 4.25342C16.0182 2.92719 14.8226 2 13.4533 2H10.5555C9.18616 2 7.99062 2.92719 7.64985 4.25342L7.22886 5.8919H4C3.44772 5.8919 3 6.33961 3 6.8919C3 7.44418 3.44772 7.8919 4 7.8919H4.10069L5.31544 19.3172C5.47763 20.8427 6.76455 22 8.29863 22H15.7014C17.2354 22 18.5224 20.8427 18.6846 19.3172L19.8993 7.8919H20C20.5523 7.8919 21 7.44418 21 6.8919C21 6.33961 20.5523 5.8919 20 5.8919H16.7799ZM17.888 7.8919H6.11196L7.30423 19.1057C7.3583 19.6142 7.78727 20 8.29863 20H15.7014C16.2127 20 16.6417 19.6142 16.6958 19.1057L17.888 7.8919ZM10 10C10.5523 10 11 10.4477 11 11V16C11 16.5523 10.5523 17 10 17C9.44772 17 9 16.5523 9 16V11C9 10.4477 9.44772 10 10 10ZM14 10C14.5523 10 15 10.4477 15 11V16C15 16.5523 14.5523 17 14 17C13.4477 17 13 16.5523 13 16V11C13 10.4477 13.4477 10 14 10Z" fill="currentColor"></path></svg></span>';

function getLink(uuid = null) {

  function handleDelIconClick(link) {
    var confirmed = confirm('Are you sure you want to delete this extractor?');
    if (!confirmed) return;
    // Step 3: Send DELETE request to the server
    // Assuming the UUID or some identifier is stored in a data attribute like 'data-uuid'
    var uuid = link.getAttribute('href');
    fetch('/extractor' + uuid, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(function (response) { return response.json(); })
      .then(function (data) {
        if (data.status === 'success') {
          console.log('Deleted successfully, uuid: ', uuid);
          getLink(); // Refresh the links
        } else {
          alert('删除失败'); // Show failure message
        }
      })
      .catch(function (error) {
        console.error('Error:', error);
        alert('删除失败'); // Show failure message in case of a network error or other failure
      });
  }

  // Function to create a link element with the given data
  function createLink(uuid, name) {
    const div = document.createElement('div');
    const a = document.createElement('a');
    a.href = '/' + uuid; // Prepend '/' to the UUID
    a.textContent = name; // Set the link text to the name
    a.innerHTML += delSvg;
    a.className = 'extractor-link';

    a.onclick = function (event) {
      event.preventDefault(); // Prevent the default link action

      // Get the position of the click
      const rect = a.getBoundingClientRect();
      const iconWidth = 24; // The width of your icon
      const iconRightPadding = 5; // The right padding you've set in your CSS
      const iconLeftBoundary = rect.right - iconWidth - iconRightPadding;
      // Check if the click was within the icon's horizontal boundaries
      if (event.clientX >= iconLeftBoundary && event.clientX <= rect.right) {
        // The click was on the icon
        handleDelIconClick(a);
        return;
      }

      var url = new URL(a.href);
      var uuid = url.pathname.split('/').pop();
      updateExtractorDetails(uuid); // Update the details based on this link

      var current = document.getElementsByClassName("extractor-link active");
      if (current.length > 0) {
        current[0].className = current[0].className.replace(" active", "");
      }
      this.className += " active";
    };

    div.appendChild(a);
    return div;
  }

  // Fetch the JSON array from the server
  fetch('/extractor')
    .then(function (response) {
      return response.json(); // Parse the JSON from the response
    })
    .then(function (data) {
      console.log(data);
      const linkWrapper = document.querySelector('.link-wrapper');
      linkWrapper.innerHTML = ''; // Clear any existing content
      extractorsData = data.data
      extractorsData.forEach(function (item) {
        div = createLink(item.uuid, item.name);
        linkWrapper.appendChild(div);
        if (uuid && item.uuid === uuid) {
          clickLink(uuid);
        }
      });

    })
    .catch(function (error) {
      console.error('Error fetching data: ', error);
    });
}

function clickLink(uuid) {
  var links = document.querySelectorAll('a.extractor-link');

  if (uuid === null) {
    //  清空所有links的active
    var current = document.getElementsByClassName("extractor-link active");
    for (let i = 0; i < current.length; i++) {
      current[i].className = current[i].className.replace(" active", "");
    }
    return;
  }

  var url = '/' + uuid;
  // Iterate over the links to find the one with the matching href
  links.forEach(function (link) {
    console.log(link.getAttribute('href'), url);
    if (link.getAttribute('href') == url) {
      // If a match is found, trigger a click on it
      console.log('click', url);
      link.click();
    }
  });
}

// Function to update the extractor details in the form
function updateExtractorDetails(uuid) {
  // Find the extractor data based on the uuid
  const extractor = extractorsData.find(item => item.uuid === uuid);
  if (extractor) {
    // Update the contenteditable element and textarea
    document.getElementById('extractor-name').textContent = extractor.name;
    document.getElementById('extractor-name').setAttribute('uuid', uuid);
    document.getElementById('prompt-text').value = extractor.instruction.trim();
  }
}

// === tab ===
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tab-list-item");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

function createButtonFun() {
  {
    // Assuming you want to send the name and description as POST data
    var extractorName = document.getElementById('extractor-name').textContent;
    var uuid = document.getElementById('extractor-name').getAttribute('uuid')
    var instruction = document.getElementById('prompt-text').value;
    console.log(extractorName, instruction, uuid);
    method = 'POST';
    if (!uuid) {
      // 新的提取器，需要检测名字是否重复
      if (extractorsData.find(item => item.name === extractorName)) {
        alert('已存在同样名字的提取器');
        return;
      }
    }
    else {
      method = 'PUT'
    }

    var data = { "name": extractorName, "instruction": instruction, "uuid": uuid };

    fetch('/extractor', {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
      .then(function (response) { return response.json(); })
      .then(function (data) {
        if (data.status === 'success') {
          getLink(data.uuid);
          alert('保存成功'); // Display success message
        } else {
          alert('保存失败'); // Display failure message
        }
      })
      .catch(function (error) {
        console.error('Error:', error);
        alert('保存失败'); // Display failure message
      });
  }
}

function initExtractorDetail() {
  document.getElementById('form-tab').innerHTML = defaultExtractorHtml;

  var contentEditable = document.getElementById('extractor-name');
  contentEditable.addEventListener('focus', function (e) {
    if (contentEditable.textContent === '') {
      contentEditable.textContent = '';
    }
  });

  contentEditable.addEventListener('blur', function (e) {
    if (contentEditable.textContent === '') {
      contentEditable.textContent = '';
    }
  });

  // === 提示词和创建按钮 ===
  var textarea = document.getElementById('prompt-text');
  var contentEditable = document.getElementById('extractor-name');
  var createButton = document.getElementById('create-button');

  // Function to toggle the button's disabled state based on textarea content
  function toggleButtonState() {
    createButton.disabled = textarea.value.trim().length < 30 || contentEditable.textContent === ''; // Disable if empty, enable if not, or if length is less than 30
  }

  // Event listener for textarea input
  textarea.addEventListener('input', toggleButtonState);
  contentEditable.addEventListener('input', toggleButtonState);
  createButton.addEventListener('click', createButtonFun);
}

function initLeftHeader() {
  var header = document.querySelector('.header');
  header.addEventListener('click', function () {
    initExtractorDetail();
    clickLink(null);
  });
}

document.addEventListener('DOMContentLoaded', function () {
  // === 获取所有提取器 ===
  getLink();

  initExtractorDetail();

  initLeftHeader();
});