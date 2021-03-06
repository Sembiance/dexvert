"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Amiga IFF Catalog",
	website        : "http://fileformats.archiveteam.org/wiki/IFF",
	ext            : [".catalog"],
	forbidExtMatch : true,
	magic          : ["IFF data, CTLG message catalog", "Amiga Catalog translation format"]
};

exports.steps = [() => ({program : "strings"})];
