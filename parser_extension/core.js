if (typeof mainTab == 'undefined') {
    // Unique ID for the className.
    MOUSE_VISITED_CLASSNAME = 'crx_mouse_visited';
    IMPORTANT_INFO = 'important_info';
    // Previous dom, that we want to track, so we can remove the previous styling.
    prevClickedDOM = null;
    selectedVariables = {};
    dom_css_selector_val = null;
    elem = null;
    pageUrl = window.location.href;
    doneButton = null;
    selectedVariablesText = null;
    swalPopup = null;
    shoppingSite = true;
    importantInfoList = [];

    //Create & inject main tab
    mainTab = createMainTab();

    function getDomFullPath(el) {
        var names = [];
        while (el.parentNode) {
            if (el.id) {
                names.unshift('#' + el.id);
                break;
            } else {
                if (el == el.ownerDocument.documentElement) names.unshift(el.tagName);
                else {
                    for (var c = 1, e = el; e.previousElementSibling; e = e.previousElementSibling, c++);
                    names.unshift(el.tagName + ":nth-child(" + c + ")");
                }
                el = el.parentNode;
            }
        }
        return names.join(" > ");
    }

    function findSpecDivOrTable(element) {
        var result;
        while (element.parentNode) {
            if (element.tagName.toLocaleLowerCase().localeCompare("div") === 0 ||
                element.tagName.toLocaleLowerCase().localeCompare("table") === 0) {
                result = element;
                break;
            } else {
                element = element.parentNode;
            }
        }
        return result;
    }

    function createSelector() {
        var selector = document.createElement('select');
        var titleOption = '<option value="title">Title</option>';
        var janOption = '<option value="jan">Jan</option>';
        var megaOption = '<option value="manufacturer">Manufacturer</option>';
        var mpnOption = '<option value="mpn">MPN</option>';
        var categoryOption = '<option value="category">Category</option>';
        var brandOption = '<option value="brand">Brand</option>';
        var releaseDateOption = '<option value="release_date">Release date</option>';
        var priceOption = '<option value="price">Price</option>';
        var regularPriceOption = '<option value="regular_price">Regular price</option>';
        var regularPriceWithTaxOption = '<option value="regular_price_with_tax">Regular price with tax</option>';
        var specialPriceOption = '<option value="special_price">Special price</option>';
        var specialPriceWithTaxOption = '<option value="special_price_with_tax">Special price with tax</option>';
        var rawDataOption = '<option value="raw_data">Raw data</option>';
        var otherOption = '<option value="Other">Others</option>';
        selector.innerHTML += titleOption;
        selector.innerHTML += janOption;
        selector.innerHTML += megaOption;
        selector.innerHTML += mpnOption;
        selector.innerHTML += categoryOption;
        selector.innerHTML += brandOption;
        selector.innerHTML += releaseDateOption;
        selector.innerHTML += priceOption;
        selector.innerHTML += regularPriceOption;
        selector.innerHTML += regularPriceWithTaxOption;
        selector.innerHTML += specialPriceOption;
        selector.innerHTML += specialPriceWithTaxOption;
        selector.innerHTML += rawDataOption;
        selector.innerHTML += otherOption;
        selector.setAttribute("class", "selector");
        selector.setAttribute("style", "margin-top: 10px;");
        return selector;
    }

    function isDescendant(parent, child) {
        var node = child.parentNode;
        while (node !== null) {
            if (node == parent || child === parent) {
                return true;
            }
            node = node.parentNode;
        }
        return false;
    }

    function createMainTab() {
        var mainTab = document.createElement('div');
        var h2 = document.createElement('h2');
        var p = document.createElement('p');
        var big = document.createElement('big');
        var doneButton = document.createElement('button');

        mainTab.setAttribute("id", "agpMainTab");
        mainTab.setAttribute("class", "mainTabStyle");
        p.setAttribute("class", "mainTabStyle-p");
        p.setAttribute("id", "selectedVariablesText");
        doneButton.setAttribute("type", "button");
        doneButton.setAttribute("id", "doneButton");
        doneButton.setAttribute("class", "mainTabDoneButton");

        h2.innerHTML = "Selected Variables";
        p.innerHTML = "None";
        // big.innerHTML = "None";
        doneButton.innerHTML = "Done";

        mainTab.appendChild(h2);
        // p.appendChild(big);
        mainTab.appendChild(p);
        mainTab.appendChild(doneButton);

        mainTab.style.display = "None";

        return mainTab;
    }

    function closePopup() {
        dom_css_selector_val = null;
        elem = null;
        prevClickedDOM.classList.remove(MOUSE_VISITED_CLASSNAME);
        popUp.style.display = "None";
    }

    function showPageImprotantInfo(jsonRes) {
        response = JSON.parse(jsonRes);
        if (response.status == "ok" && typeof response.errors === 'undefined') {
            item = response.items[0];
            if (item.status == "successful") {
                swal.close(); //Close loading popup

                title = item.title;
                prices = item.price;
                jan = item.jan_code;
                manufactureres = item.manufacturer;

                highlightImportantInfo(title);
                highlightImportantInfo(prices);
                highlightImportantInfo(jan);
                highlightImportantInfo(manufactureres);
            } else {
                swal("Error", "Failed to automatically analyze and retrieve the suggested info", "error");
            }
        } else {
            swal("Error", "Failed to read the webpage", "error");
        }
    }

    function findPageImportantInfo(pageUrl) {
        destUrl = "http://127.0.0.1:8000/crawl.json?spider_name=ecjido3&url=" + pageUrl;
        var xmlHttp = new XMLHttpRequest();
        try {
            xmlHttp.onreadystatechange = function() {
                if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
                    showPageImprotantInfo(xmlHttp.responseText);
                    showMainTab();
                } else if (xmlHttp.readyState == 4 && xmlHttp.status == 0) {
                    swal("Error", "Failed to connect to ecjido system", "error");
                    showMainTab();
                }
            };
            xmlHttp.open("GET", destUrl, true); // true for asynchronous
            xmlHttp.send();
        } catch (e) {
            console.error('catch', e);
        }
    }

    function highlightImportantInfo(elem) {
        if (elem != "-" && elem.length !== 0) {
            if (typeof elem === 'object') {
                for (var i = 0; i < elem.length; ++i) {
                    dom = document.querySelector(elem[i]);
                    dom.classList.add(IMPORTANT_INFO);
                    importantInfoList.push(dom);
                }
            } else {
                dom = document.querySelector(elem);
                dom.classList.add(IMPORTANT_INFO);
                importantInfoList.push(dom);
            }
        }
    }

    function unhighlightImportantInfo(importantInfoList) {
        for (i = 0; i < importantInfoList.length; i++) {
            dom = importantInfoList[i];
            dom.classList.remove(IMPORTANT_INFO);
        }
    }

    function analyzeWebpage() {
        //Show loading
        swal({
            title: "Analyzing webpage",
            text: '<div class="injectedLoader" id="spinner">Loading</div>',
            html: true,
            showConfirmButton: false,
            allowEscapeKey: false,
            timer: 1 // Timer is necessary to make swal automatically call callback func
        }, function() {
            //Connect to ecjido system, analyze the webpage and show improtant page info that users might want to parse
            findPageImportantInfo(pageUrl);
        });
    }

    function showMainTab() {
        mainTab.style.display = "";
    }

    function hideMainTab() {
        mainTab.style.display = "None";
    }

    function isMainTabDisplayed() {
        if (mainTab.style.display === "") {
            return true;
        } else {
            return false;
        }
    }

    function onClickFunc(event) {
        //Prevent <a> navigation
        event.preventDefault();

        //Declara the dom of injected sweetalert popup for mouse click checking purpose
        if (swalPopup === null) {
            swalPopup = document.querySelector("div.sweet-alert");
        }

        var srcElement = event.srcElement;
        //if users didn't click on an element inside the popup
        if (!isDescendant(popUp, srcElement) && !isDescendant(mainTab, srcElement) && !isDescendant(swalPopup, srcElement)) {
            if (prevClickedDOM !== null) {
                prevClickedDOM.classList.remove(MOUSE_VISITED_CLASSNAME);
            }
            // Add a visited class name to the element. So we can style it.
            srcElement.classList.add(MOUSE_VISITED_CLASSNAME);

            // The current element is now the previous. So we can remove the class
            // during the next iteration.
            prevClickedDOM = srcElement;

            //Get css selector of the element
            dom_css_selector_val = getDomFullPath(srcElement);

            //Query the the given css selector for checking the result
            elem = document.querySelector(dom_css_selector_val);

            //Visible popup, update position and info of the popup
            showPopup(event.pageX, event.pageY, dom_css_selector_val, elem.textContent);
        } else {
            //if Ok button is clicked
            if (okButton == srcElement) {
                //Check whether it's shopping site or not
                if (shoppingSite) {
                    //Check whether any element is selected or not
                    if (dom_css_selector_val === null) {
                        swal("Error", "You didn't select any element", "error");
                    } else {
                        var keyName;
                        //If others is selected, get the new category name
                        if (selector.value.localeCompare("Other") === 0) {
                            if (otherInputBox.value !== "") {
                                keyName = otherInputBox.value;
                            } else {
                                swal("Error", "You didn't type new category name", "error");
                            }
                        } else {
                            keyName = selector.options[selector.selectedIndex].value;
                        }
                        try {
                            if (!isValueExisted(keyName)) {
                                storeValue(keyName, dom_css_selector_val, elem.textContent);
                                swal("Stored!!", keyName + " has been stored", "success");
                            } else {
                                swal({
                                    title: keyName + " is already existed",
                                    text: "Do you want to replace?",
                                    type: "warning",
                                    showCancelButton: true,
                                    confirmButtonColor: "#DD6B55",
                                    confirmButtonText: "Replace",
                                    closeOnConfirm: false
                                }, function() {
                                    storeValue(keyName, dom_css_selector_val, elem.textContent);
                                    swal("Replaced!", keyName + " has been replaced", "success");
                                });
                            }
                        } catch (e) {
                            swal("Error", "Something is wrong, plese see console log", "error");
                            console.error(e);
                        }
                    }
                } else {
                    //Check whether any element is selected or not
                    if (dom_css_selector_val === null) {
                        swal("Error", "You didn't select any element", "error");
                    } else {
                        var keyName;
                        if (otherInputBox.value !== "") {
                            keyName = otherInputBox.value;
                            try {
                                if (isValueExisted(keyName)) {
                                    swal({
                                        title: keyName + " is already existed",
                                        text: "Do you want to replace?",
                                        type: "warning",
                                        showCancelButton: true,
                                        confirmButtonColor: "#DD6B55",
                                        confirmButtonText: "Replace",
                                        closeOnConfirm: false
                                    }, function() {
                                        storeValue(keyName, dom_css_selector_val, elem.textContent);
                                        swal("Replaced!", value + " has been replaced", "success");
                                    });
                                } else {
                                    storeValue(keyName, dom_css_selector_val, elem.textContent);
                                    swal("Stored!!", keyName + " has been stored", "success");
                                }
                            } catch (e) {
                                swal("Error", "Something is wrong, plese see console log", "error");
                                console.error(e);
                            }
                        } else {
                            swal("Error", "You didn't type new category name", "error");
                        }
                    }
                }
            } else if (cancelButton == srcElement) {
                closePopup();
            } else if (doneButton == srcElement) {
                if (Object.keys(selectedVariables).length === 0) {
                    swal("Error", "You haven't selected any variables", "error");
                } else {
                    if (!shoppingSite) {
                        swal({
                            title: "Found a new template!",
                            text: "Do you want to save <big><b>" + Object.keys(selectedVariables) + "</b></big> as a new templete?",
                            type: "warning",
                            showCancelButton: true,
                            confirmButtonColor: "#DD6B55",
                            confirmButtonText: "Yes, save it!",
                            cancelButtonText: "No, thanks",
                            closeOnConfirm: false,
                            closeOnCancel: false,
                            html: true
                        }, function(isConfirm) {
                            if (isConfirm) {
                                getNewTempleteName();
                            } else {
                                confirmFinish();
                            }
                        });
                    } else {
                        confirmFinish();
                    }
                }
            }
        }
    }

    function confirmFinish() {
        swal({
            title: "Finished?",
            text: "Finished collecting everything you want?",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Finished",
            closeOnConfirm: true
        }, function() {
            //Also send page html and type of website for further processes
            selectedVariables.pageHtml = document.documentElement.outerHTML;
            selectedVariables.shoppingSite = shoppingSite;
            chrome.runtime.sendMessage(selectedVariables);
        });
    }

    function storeNewTemplete(newTemplete) {
        var obj = {};
        obj[newTemplete] = Object.keys(selectedVariables);
        chrome.storage.sync.set(obj, function() {
            swal({
                title: "Nice!",
                text: "Your templete: " + newTemplete + " has been saved",
                type: "success",
                showCancelButton: true,
                closeOnConfirm: false
            }, function() {
                confirmFinish();
            });
        });
    }

    function createTempleteSelector(templetes) {
        var selector = document.createElement('select');
        selector.innerHTML += '<option value="shopping">shopping</option>'
        for (tem in templetes) {
            selector.innerHTML += `<option value="${tem}">${tem}</option>`
        }
        selector.setAttribute("id", "templeteSelector");
        return selector;
    }

    function getTempleteList() {
        chrome.storage.sync.get(null, chooseTemplete);
    }

    function getNewTempleteName() {
        swal({
            title: "Templete name",
            text: "Define your new templete name",
            type: "input",
            closeOnConfirm: false,
            animation: "slide-from-top",
            inputPlaceholder: "Templete name"
        }, function(inputValue) {
            if (inputValue === false) return false;
            if (inputValue === "") {
                swal.showInputError("You need to write something!");
                return false
            }
            storeNewTemplete(inputValue);
        });
    }

    function chooseTemplete(templetes) {
        var span = document.createElement('span');
        span.appendChild(createTempleteSelector(templetes));
        swal({
            title: "Choose Parser Templete",
            text: span.innerHTML,
            html: true,
            showConfirmButton: true,
            closeOnConfirm: false,
            allowEscapeKey: false
        }, function () {
            var templeteSelector = document.getElementById("templeteSelector");
            var templateName = templeteSelector.options[templeteSelector.selectedIndex].value;
        });
    }

    function onPopUpSelectorChange() {
        if (selector.value.localeCompare("Other") === 0) {
            otherInputBoxSpan.style.display = "";
            otherInputBox.value = "";
        } else {
            otherInputBoxSpan.style.display = "none";
        }
    }

    //Activate all event listeners
    function activateEventListeners() {
        //All page click listener
        document.addEventListener('click', onClickFunc);

        //Enable this selector event listener in case a shopping site
        if (shoppingSite) {
            //When "other" is selected, insert an input box
            selector.addEventListener('change', onPopUpSelectorChange);
        }
    }

    //Deactivate all eventlisteners
    function deactivateEventListeners() {
        document.removeEventListener('click', onClickFunc);
        if (shoppingSite) {
            selector.removeEventListener('change', onPopUpSelectorChange);
        }
    }

    function askAboutTemplete() {
        if (window.swal) {
            //Asking popup
            swal({
                title: "Use existing templete?",
                text: "Do you want to use existing templetes?",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Yes",
                cancelButtonText: "No, create new",
                closeOnConfirm: false
            }, function(isConfirm) {
                if (isConfirm) {
                    shoppingSite = true;
                    createTempleteSelector();
                    // Create & Inject pop up into the website
                    popUp = createPopup();
                    document.body.appendChild(popUp);
                    //Start analyzing webpage
                    analyzeWebpage();
                    activateEventListeners();
                } else {
                    shoppingSite = false;
                    // Create & Inject pop up into the website
                    popUp = createPopup();
                    document.body.appendChild(popUp);
                    //Show main tab and activate listener;
                    showMainTab();
                    activateEventListeners();
                }
            });
        } else {
            window.setTimeout(function() {
                askAboutTemplete();
            }, 100);
        }
    }

    //Create main popup
    function createPopup() {
        var popUp = document.createElement('div');
        stylePopUp(popUp);
        return popUp;
    }

    //Styling main popup
    function stylePopUp(popUp) {
        selectedElementInfo = document.createElement('dl');
        var infoSpan = document.createElement('span');
        okButton = document.createElement('input');
        cancelButton = document.createElement('input');
        otherInputBoxSpan = document.createElement('span');
        var otherInputBoxLabel = document.createElement('label');
        otherInputBox = document.createElement('input');

        //Styling ok and cancel buttons
        okButton.setAttribute("type", "button");
        okButton.setAttribute("name", "ok");
        okButton.setAttribute("value", "ok");
        okButton.style.margin = "0px 0px 0px 5px";
        okButton.style.display = "inline-block";
        cancelButton.setAttribute("type", "button");
        cancelButton.setAttribute("name", "cancel");
        cancelButton.setAttribute("value", "cancel");
        cancelButton.style.display = "inline-block";

        //Styling other span part (For adding new variables)
        otherInputBoxSpan.style.display = "none";
        otherInputBoxLabel.setAttribute("class", "bold");
        otherInputBoxLabel.setAttribute("for", "otherInputBox");
        otherInputBoxLabel.innerHTML = 'Type new category name : ';
        otherInputBox.setAttribute("id", "otherInputBox");
        otherInputBox.setAttribute("type", "text");
        otherInputBox.setAttribute("class", "otherBox");
        otherInputBoxSpan.appendChild(otherInputBoxLabel);
        otherInputBoxSpan.appendChild(otherInputBox);
        //If it's a shopping site, add selector into popup
        if (shoppingSite) {
            var selectorSpan = document.createElement('span');
            var selectorLabel = document.createElement('label');
            selector = createSelector();
            selectorLabel.setAttribute("class", "bold");
            selectorLabel.setAttribute("for", "selector");
            selectorLabel.innerHTML = 'Map to : ';
            selectorSpan.appendChild(selectorLabel);
            selector.style.display = "inline-block";
            selectorSpan.appendChild(selector);
            selectorSpan.appendChild(okButton);
            selectorSpan.appendChild(cancelButton);

            popUp.appendChild(infoSpan);
            popUp.appendChild(selectorSpan);
            popUp.appendChild(otherInputBoxSpan);
        } else {
            otherInputBoxSpan.appendChild(okButton);
            otherInputBoxSpan.appendChild(cancelButton);
            otherInputBoxSpan.style.display = "";
            otherInputBox.value = "";
            popUp.appendChild(infoSpan);
            popUp.appendChild(otherInputBoxSpan);
        }

        infoSpan.appendChild(selectedElementInfo);
        popUp.setAttribute("id", "popup-window");
        popUp.setAttribute("style", "max-width: 400px; display: None;");

        return popUp
    }

    function showPopup(positionX, positionY, elemTag, elemResult) {
        popUp.style.display = "";
        popUp.style.left = positionX + "px";
        popUp.style.top = (positionY + 30) + "px";
        otherInputBox.value = "";
        selectedElementInfo.innerHTML = "";
        selectedElementInfo.innerHTML += "<dt class='bold'>Selected element tag : </dt><dd>" + elemTag + "</dd></br>";
        selectedElementInfo.innerHTML += "<dt class='bold'>Selected element result : </dt><dd>" + elemResult + "</dd>";
    }

    function injectMainTab(mainTab) {
        document.body.appendChild(mainTab);
        document.body.classList.add("toolbar");
    }

    //Check whether variable has already existed in obj or not. If not, it will be added to obj.
    function isValueExisted(value) {
        if (!(value in selectedVariables)) {
            return false;
        }
        return true;
    }

    function storeValue(keyName, elemVal, elemCSS) {
        //if variable is spec, find the first table or div parent of the element
        if (keyName.localeCompare("raw_data") == 0) {
            var elemCSS = getDomFullPath(findSpecDivOrTable(prevClickedDOM));
            var elemVal = document.querySelector(elemCSS);
            selectedVariables[keyName] = {
                css: elemCSS,
                value: elemVal.textContent
            };
        } else {
            selectedVariables[keyName] = {
                css: elemCSS,
                value: elemVal
            };
        }
        closePopup();
        selectedVariablesText.innerHTML = Object.keys(selectedVariables);
    }

    //Hide all DOM created by extension
    function hide() {
        hideMainTab();
        if (isPopUpDisplayed()) {
            closePopup();
        }
        if (importantInfoList.length != 0) {
            unhighlightImportantInfo(importantInfoList);
        }
        swal.close();
    }

    //Reset all data and DOM to default
    function restoreToDefault() {
        document.body.classList.remove("toolbar");
        selectedVariablesText.innerHTML = "None";

        prevClickedDOM = null;
        selectedVariables = {};
        dom_css_selector_val = null;
        pageUrl = window.location.href;
        elem = null;
        doneButton = null;
        selectedVariablesText = null;
        swalPopup = null;
        shoppingSite = true;
        importantInfoList = [];
    }

    function isPopUpDisplayed() {
        if (popUp.style.display === "") {
            return true;
        } else {
            return false;
        }
    }
}

if (!isMainTabDisplayed()) {
    injectMainTab(mainTab);
    doneButton = document.getElementById("doneButton");
    selectedVariablesText = document.getElementById("selectedVariablesText");
    askAboutTemplete();
} else {
    hide();
    deactivateEventListeners();
    restoreToDefault();
}
