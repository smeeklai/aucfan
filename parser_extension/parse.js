var domain = "zozo";

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
var columns = {
        "title":"#item-intro > H1:nth-child(2)",
        "jan":"", // 45 o9 から始まる13桁の数字
        "manufacturer":"",
        "mpn":"", // 型番
        "category":"", // パンくず、カンマ区切り。Homeとか、トップみたいな単語は削る
        "brand":"",
        "release_date":"", // String dateに直せないものもあるので
        "price":"", // 実際の販売価格。"税込","$",","などは削除
        "regular_price":"", // 定価
        "regular_price_with_tax":"",
        "special_price":"", // 特価、セール価格など
        "special_price_with_tax":"",
        "raw_data":"", // スペックとしてうまく取れないやつを,htmlタグ込でそのまま保存
};
var item = {};
item["timestamp"] = Date.parse(d); // httpresponseのdate

for(var k in columns) {
  if (k == "raw_data") {
    try {
        item[k] = root.findOne(columns[k]).innerHTML();
    } catch (e) {
        item[k] = "";
    }
  } else {
    try {
        item[k] = root.findOne(columns[k]).text().trim();
    } catch (e) {
        item[k] = "";
    }
  }
}

//Getting category
// item["category"] = "";

// get from uri
uri = "http://zozo.jp/shop/bapeland/goods/11786701/?did=27260319"
item["uri"] = uri;
item["source"] = uri.split('/')[2];
item["source_id"] = 11786701;

//additional modification
//If you would like to modify or add any special processes, functions other than how the script normally works, please write your code down below

// post-process
//You might add more post-process functions which haven't provided below
item["source"]= item["source"].replace(/\./g, '_');

var items = {};
var file_pattern = item["source_id"];

var prefix = domain + '/.' + today + '/' + file_pattern + '.json';

items[prefix] = JSON.stringify(item);