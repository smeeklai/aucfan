//Global variables section
var variables;
var senderUrl;
var pageHtml;
var shoppingSite;
var postProcessCodeArea;
var sourceId = "";
var sourceIdCodeArea = null;
var scriptCodeArea = null;
var resultCodeArea = null;
var scriptDownloadButton;
var fileName = "parse.js";
var additionalModiCodeArea;
var highlightingRadioButton;
var manuallyCodingRadioButton;
var codeSyncronizationMode = false;
var resultDiv;
var resultTextAreaDiv;
var spinner;

//String section
var additionalModiCodeAreaIntro = "//If you would like to modify or add any special processes, functions other than how the script normally works, please write your code down below";
var postProcessCodeAreaIntro = "//You might add more post-process functions which haven't provided below";

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  variables = request.variables;
  senderUrl = request.senderUrl;
  pageHtml = request.html;
  shoppingSite = request.isShoppingSite;

  if (typeof variables != 'undefined') {
    showSelectedVariables(variables);
    setTextToCodeArea(postProcessCodeArea, createPostProcessCode(variables));
  }
});

window.addEventListener("load",function(){
    //Variables declaration
    resultDiv = document.getElementById("resultDiv");
    resultTextAreaDiv = document.getElementById("resultTextAreaDiv");
    spinner = document.getElementById("spinner");

    //Send message to inform background.js after the page has done loading
    chrome.runtime.sendMessage({load: "done"});

    //Initialize code areas
    additionalModiTextArea =
    additionalModiCodeArea = transformTextAreaToCodeArea("additionalModiTextArea");
    setTextToCodeArea(additionalModiCodeArea, additionalModiCodeAreaIntro);
    postProcessCodeArea = transformTextAreaToCodeArea("postProcessTextArea");

    //Initialize Source ID area
    highlightingRadioButton = document.getElementById("highlightingRadioButton");
    manuallyCodingRadioButton = document.getElementById("manuallyCodingRadioButton");
    highlightingRadioButton.onchange = function(){createSourceId(highlightingRadioButton, manuallyCodingRadioButton);};
    manuallyCodingRadioButton.onchange = function(){createSourceId(highlightingRadioButton, manuallyCodingRadioButton);};

    //Add script buttons listener
    addDownloadScriptButtonListener();
    addShowScriptButtonListener();
    addTestScriptButtonListener();
});

function getScriptContent() {
  var domain = document.getElementById("websiteName").value;
  var urlCode;
  if (highlightingRadioButton.checked) {
    sourceIdCode = createSourceIdCode(sourceId);
    urlCode = getUrlCode(sourceIdCode);
  } else if (manuallyCodingRadioButton.checked) {
    sourceIdCode = getCodeFromCodeArea(sourceIdCodeArea);
    urlCode = getUrlCode(sourceIdCode);
  }
  var additionalModificationCode = getCodeFromCodeArea(additionalModiCodeArea);
  var postProcessCode = getCodeFromCodeArea(postProcessCodeArea);
  var columnCode = getColumnCode(variables);
  var categoryCode = getCategoryCode(variables);
  return createScripContent(domain, columnCode, categoryCode, urlCode, additionalModificationCode, postProcessCode);
}

//Create sourceIdCode from user's selected sourceId
function createSourceIdCode(sourceId){
  slashSeparatedArray = senderUrl.split("/");
  indexOfSourceIdInUrl = slashSeparatedArray.indexOf(sourceId);
  result = `item["source_id"] = url.split('/')[${indexOfSourceIdInUrl}];`;
  return result;
}

//Create column code
function getColumnCode(obj) {
  var tempVariables = $.extend(true,{},obj);
  var columnCode = `var columns = {`;
  if (shoppingSite) {
    columnCode = `var columns = {
      "title":"${tempVariables.title ? tempVariables.title.css : ""}",
      "jan":"${tempVariables.jan ? tempVariables.jan.css : ""}", // 45 o9 から始まる13桁の数字
      "manufacturer":"${tempVariables.manufacturer ? tempVariables.manufacturer.css : ""}",
      "mpn":"${tempVariables.mpn ? tempVariables.mpn.css : ""}", // 型番
      "category":"${tempVariables.category ? tempVariables.category.css : ""}", // パンくず、カンマ区切り。Homeとか、トップみたいな単語は削る
      "brand":"${tempVariables.brand ? tempVariables.brand.css : ""}",
      "release_date":"${tempVariables.release_date ? tempVariables.release_date.css : ""}", // String dateに直せないものもあるので
      "price":"${tempVariables.price ? tempVariables.price.css : ""}", // 実際の販売価格。"税込","$",","などは削除
      "regular_price":"${tempVariables.regular_price ? tempVariables.regular_price.css : ""}", // 定価
      "regular_price_with_tax":"${tempVariables.regular_price_with_tax ? tempVariables.regular_price_with_tax.css : ""}",
      "special_price":"${tempVariables.special_price ? tempVariables.special_price.css : ""}", // 特価、セール価格など
      "special_price_with_tax":"${tempVariables.special_price_with_tax ? tempVariables.special_price_with_tax.css : ""}",
      "raw_data":"${tempVariables.raw_data ? tempVariables.raw_data.css : ""}", // スペックとしてうまく取れないやつを,htmlタグ込でそのまま保存,`

    // Delete the default variables in order to loop through the new added variables only
    delete tempVariables.title;
    delete tempVariables.jan;
    delete tempVariables.manufacturer;
    delete tempVariables.mpn;
    delete tempVariables.category;
    delete tempVariables.brand;
    delete tempVariables.release_date;
    delete tempVariables.price;
    delete tempVariables.regular_price;
    delete tempVariables.regular_price_with_tax;
    delete tempVariables.special_price;
    delete tempVariables.special_price_with_tax;
    delete tempVariables.raw_data;
  }

  //Add new variables if existed
  try {
    for (var key in tempVariables) {
      columnCode += '\n\t"' + key + '":"' + tempVariables[key].css + '",';
    }
    columnCode += "\n};";
  } catch (e) {
    console.error(e);
  }
  return columnCode;
}

//Show selected variables to user
function showSelectedVariables(variables) {
  var varTable = document.getElementById("variableTable");
  var varTbody = document.createElement('tbody');
  var counter = 0;
  for (var key in variables) {
    if (variables.hasOwnProperty(key)) {
      counter++;
      var varTR = document.createElement('tr');
      varTR.innerHTML += "<th scope='row'>" + counter + "</th>";
      varTR.innerHTML += "<td>" + key + "</td>";
      varTR.innerHTML += "<td>" + variables[key].css + "</td>";
      varTR.innerHTML += "<td>" + variables[key].value + "</td>";
      varTbody.appendChild(varTR);
    }
  }
  varTable.appendChild(varTbody);
}

//Return string of post-process code automatically generated by program
function createPostProcessCode(variables) {
  var price = "price";
  var regularPrice = "regular_price";
  var regularPriceWithTax = "regular_price_with_tax";
  var specialPrice = "special_price";
  var specialPriceWithTax = "special_price_with_tax";
  var cat = "category";
  var code = postProcessCodeAreaIntro;

  for (var key in variables) {
    switch (key) {
      case price:
        code += `\nitem["price"] = parseInt(item["price"].replace(/\\D+/g, ''));`;
        break;
      case regularPrice:
        code += `\nitem["regular_price"] = parseInt(item["regular_price"].replace(/\\D+/g, ''));`;
        break;
      case regularPriceWithTax:
        code += `\nitem["regular_price_with_tax"] = parseInt(item["regular_price_with_tax"].replace(/\\D+/g, ''));`;
        break;
      case specialPrice:
        code += `\nitem["special_price"] = parseInt(item["special_price"].replace(/\\D+/g, ''));`;
        break;
      case specialPriceWithTax:
        code += `\nitem["special_price_with_tax"] = parseInt(item["special_price_with_tax"].replace(/\\D+/g, ''));`;
        break;
      default:
        code += "";
        break;
    }
  }
  var source = `\nitem["source"]= item["source"].replace(/\\./g, '_');`;
  code += source;
  return code;
}

function validtate() {
  var domain = document.getElementById("websiteName").value;
  if (domain !== "") {
    if ((highlightingRadioButton.checked || manuallyCodingRadioButton.checked) && sourceId !== "") {
      return true;
    } else {
      swal("Error", "Source ID is not specified", "error");
    }
  } else {
    swal("Error", "Website Name is not specified", "error");
  }
  return false;
}

function setTextToCodeArea(codeArea, text) {
  codeArea.setValue(text);
}

function startDownloader(fileName, scriptContent) {
  var url = "data:text/plain;charset=utf-8," + encodeURIComponent(scriptContent);
  scriptDownloadButton.setAttribute("download", fileName);
  scriptDownloadButton.setAttribute("href", url);
  // var fileData = [scriptContent];
  // blobObject = new Blob(fileData);
  // window.navigator.msSaveOrOpenBlob(blobObject, fileName);
}

function transformTextAreaToCodeArea(textAreaId) {
  var codeMirror;
  if (textAreaId.localeCompare("scriptTextArea") === 0) {
    codeMirror = CodeMirror.fromTextArea(document.getElementById(textAreaId), {
                    mode: "javascript",
                    lineNumbers: true,
                    matchBrackets: true,
                    lineWrapping: true,
                    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
                    theme: "dracula",
                    readOnly: true
    });
  } else {
    codeMirror = CodeMirror.fromTextArea(document.getElementById(textAreaId), {
                    mode: "javascript",
                    lineNumbers: true,
                    matchBrackets: true,
                    lineWrapping: true,
                    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
                    theme: "dracula"
    });
  }
  return codeMirror;
}

function getCodeFromCodeArea(codeArea) {
  return codeArea.getValue();
}

function addClearingSourceIdListener() {
  document.getElementById("clearSourceId").onclick = function() {
    document.getElementById("sourceId").innerHTML = "Source ID: ";
    sourceId = "";
  };
}

function addShowScriptButtonListener() {
  var showScriptButton = document.getElementById("showScriptButton");
  var scriptTextAreaDiv = document.getElementById("scriptTextAreaDiv");
  var additionalModiTextAreaDiv = document.getElementById("additionalModiTextAreaDiv");
  var postProcessTextAreaDiv = document.getElementById("postProcessTextAreaDiv");
  showScriptButton.onclick = function() {
    if (showScriptButton.innerHTML.toLocaleLowerCase().localeCompare("hide script") === 0) {
      scriptTextAreaDiv.style.display = "none";
      showScriptButton.innerHTML = "Show Script"
      postProcessTextAreaDiv.style.display = "";
      additionalModiTextAreaDiv.style.display = "";
    } else {
      if(validtate()) {
        //Display div
        showScriptButton.innerHTML = "Hide Script"
        scriptTextAreaDiv.style.display = "";
        postProcessTextAreaDiv.style.display = "none";
        additionalModiTextAreaDiv.style.display = "none";

        //Initialize code area
        if (scriptCodeArea === null) {
          scriptCodeArea = transformTextAreaToCodeArea("scriptTextArea");
          scriptCodeArea.setSize(null, 500);
        }
        var currentScriptCode = getScriptContent();
        setTextToCodeArea(scriptCodeArea, currentScriptCode);
      }
    }
  };
}

function addDownloadScriptButtonListener() {
  scriptDownloadButton = document.getElementById("downloadScriptButton");
  scriptDownloadButton.onclick = function() {
    if(validtate()) {
      var content = getScriptContent();
      startDownloader(fileName, content);
    }
  };
}

function addTestScriptButtonListener() {
  document.getElementById("testScriptButton").onclick = function() {
    if(validtate()) {
      var formData = new FormData();
      var content = getScriptContent();
      var scriptBlob = new Blob([content], { type: "text/javascript"});
      var pageHtmlBlob = new Blob([pageHtml], { type: "text/html"});

      //Show loading animation
      resultDiv.style.display = "";
      spinner.style.display = "";
      resultTextAreaDiv.style.display = "none";

      formData.append("html", pageHtmlBlob);
      formData.append("script", scriptBlob);
      $.ajax({
          url: 'http://api.crawler.aucfanlab.com/support/check/script',
          data: formData,
          cache: false,
          contentType: false,
          processData: false,
          type: 'POST',
          error: function(xhr,status,error) {
            swal("Error", error, "error");
            resultDiv.style.display = "none";
            spinner.style.display = "none";
          },
          success: function(data){
              //Get the real object we wanted from the returned API result
              result = JSON.parse(data.result);
              result = result[Object.keys(result)[0]];
              showTestResult(JSON.stringify(JSON.parse(result), null, 4));
          },
      });
    }
  };
}

function addUrlSelectionListener(url) {
  var prevSelection = "";
  url.onmouseup = function(e) {
    var selection;
    if (window.getSelection) {
      selection = window.getSelection();
    }
    if (selection.toString() !== ''){
      if (selection.toString().localeCompare(prevSelection) == 0) {
        document.getElementById("sourceId").innerHTML = "Source ID: ";
        prevSelection = "";
        sourceId = "";
      } else {
        sourceId = selection.toString();
        document.getElementById("sourceId").innerHTML = "Source ID: " + sourceId;
        prevSelection = selection.toString();
      }
    } else {
      document.getElementById("sourceId").innerHTML = "Source ID: ";
      sourceId = "";
    }
  };
}

function showTestResult(result) {
  //Close loading animation
  spinner.style.display = "none";
  resultTextAreaDiv.style.display = "";

  //Initialize code area
  if (resultCodeArea === null) {
    resultCodeArea = transformTextAreaToCodeArea("resultTextArea");
    resultCodeArea.setSize(null, 400);
  }
  setTextToCodeArea(resultCodeArea, result);
}

function createSourceId(highlightingRadioButton, manuallyCodingRadioButton) {
  if (highlightingRadioButton.checked){
    //Assign url value to element
    var url = document.getElementById("url");
    url.innerHTML = "URL: " + senderUrl;
    document.getElementById("sourceIdTextAreaDiv").style.display = "None";
    document.getElementById("urlDiv").style.display = "";

    addUrlSelectionListener(url);
    addClearingSourceIdListener();
  } else if (manuallyCodingRadioButton.checked){
    document.getElementById("urlDiv").style.display = "None";
    document.getElementById("sourceIdTextAreaDiv").style.display = "";

    //Transform textArea to codeArea
    if (sourceIdCodeArea === null) {
      sourceIdCodeArea = transformTextAreaToCodeArea("sourceIdTextArea");
      var sourceIdCodeAreaPreSetText = `var sourceId = //write your code from here\nitem["source_id"] = sourceId;`;
      sourceIdCodeArea.setValue(sourceIdCodeAreaPreSetText);
    }
  }
}

function getCategoryCode(variables) {
  if (shoppingSite) {
    return `var category_css = "${variables.category ? variables.category.css : ""}";
try {
  var result = [];
  var anchors = root.findOne(category_css).find("a");
  for (var i = 0; i < anchors.length; i++) {
    result.push(anchors[i].text().trim());
  }
  item["category"] = result;
} catch (e) {
  item["category"] = "";
}`
  } else {
    return "";
  }
}

function getUrlCode(sourceId) {
  return `var url = "";
try {
  url = root.findOne('link[rel=\"canonical\"]').attr("href");
} catch(e) {
  try {
    url = root.findOne('meta[property=\"og:url\"]').attr("content");
  } catch (e) {
    url = ctx.httpResponse.getUrl().toString();
  }
}
item["url"] = url;
item["source"] = url.split('/')[2];
${sourceId}`;
}

//Reuturn completed script content
function createScripContent(domain, columnCode, categoryCode, urlCode, additionalModificationCode, postProcessCode) {
  var scriptText = `var domain = "${domain}";

var root = ctx.rootNode;
var res = ctx.httpResponse.headers;
var ap = ctx.assignedParameters;

var zerofill2 = function(num) {
  return ("00"+num).slice(-2);
}

var d = res.get("Date");
var date = new Date(d);
var today = date.getFullYear()+zerofill2(date.getMonth()+1)+zerofill2(date.getDate());

// required
// なければnullではなく""で
${columnCode}

var item = {};
item["timestamp"] = Date.parse(d); // httpresponseのdate

for(var k in columns) {
    try {
        // 再帰的にNodeExplorerでfind
        var selectors = columns[k].split(/(?: +>)? +/);
        for (var i = 0; i < selectors.length; ++i) {
            if(i == 0) {
              item[k] = root.findOne(selectors[i]);
              continue;
            }
            item[k] = item[k].findOne(selectors[i]);
        }
        if (k.localeCompare("raw_data") === 0) {
          item[k] = item[k].innerHTML();
        } else {
          item[k] = item[k].text().trim();
        }
    } catch (e) {
        item[k] = "";
    }
}

//Getting category
${categoryCode}

//Source and SourceId (Please don't delete comments)
${urlCode}

//end of source and sourceId (Please don't delete comments)

//additional modification (Please don't delete comments)
${additionalModificationCode}

//end of additional modification (Please don't delete comments)

//post-process (Please don't delete comments)
${postProcessCode}


//end of post-process (Please don't delete comments)

var items = {};
var file_pattern = item["source_id"];

var prefix = domain + '/.' + today + '/' + file_pattern + '.json';

items[prefix] = JSON.stringify(item);`;
  return scriptText;
}
