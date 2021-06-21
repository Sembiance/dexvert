"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://winworldpc.com/product/ibm-storyboard/live-20",
	unsafe  : true
};

exports.dos = () => "SBLIVE/SHOWPIC.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.dosData = state => ({keys : ["Escape"], keyOpts : {delay : XU.SECOND*15}, screenshot : {filePath : path.join(state.output.absolute, `${state.input.name}.png`), frameLoc : 100}});
