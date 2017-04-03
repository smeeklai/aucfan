chrome.browserAction.onClicked.addListener(function(tab) {
    chrome.tabs.insertCSS(tab.id, { file: "core.css" });
    chrome.tabs.executeScript(tab.id, { file: "core.js" });
    chrome.tabs.insertCSS(tab.id, { file: "node_modules/sweetalert/dist/sweetalert.css" });
    chrome.tabs.executeScript(tab.id, { file: "node_modules/sweetalert/dist/sweetalert.min.js" });
    chrome.tabs.insertCSS(tab.id, { file: "spinner.css" });
});

var pageHtml;
var shoppingSite;
var vars;
var url;
var tabID;
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (sender.url.indexOf("createScriptPage.html") > -1) {
      chrome.tabs.sendMessage(tabID, {variables : vars, senderUrl : url, html : pageHtml, isShoppingSite : shoppingSite});
    } else {
      chrome.tabs.create({url: 'createScriptPage.html'}, function (tab) {
        pageHtml = request.pageHtml;
        shoppingSite = request.shoppingSite;
        delete request.pageHtml;
        delete request.shoppingSite;
        vars = request;
        url = sender.tab.url;
        tabID = tab.id;
      });
    }
});
