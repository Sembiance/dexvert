"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "IBM Storboard PIC",
	website        : "https://winworldpc.com/product/ibm-storyboard/live-20",
	ext            : [".pic"],
	forbidExtMatch : true,
	magic          : ["IBM Storyboard bitmap"]
};

exports.converterPriorty = ["storyboardLiveShowPic"];
