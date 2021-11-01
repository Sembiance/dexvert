"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "PrintMaster Shape",
	website        : "http://fileformats.archiveteam.org/wiki/PrintMaster",
	ext            : [".shp"],
	forbidExtMatch : true,
	filesOptional  : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.sdr`),
	magic          : ["Printmaster Shape bitmap"]
};

exports.converterPriority = [{program : "deark", flags : state => ({dearkFile2 : (state.extraFilenames || []).find(v => v.toLowerCase().endsWith(".sdr"))})}];
