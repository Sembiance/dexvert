"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Print Shop Graphic POG Archive",
	website       : "http://fileformats.archiveteam.org/wiki/The_Print_Shop",
	ext           : [".pog"],
	filesOptional : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.pnm`),
	magic         : ["The Print Shop graphic"]
};

exports.converterPriorty = [{program : "deark", flags : state => ({dearkFile2 : (state.extraFilenames || []).find(v => v.toLowerCase().endsWith(".pnm"))})}];
