"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "dBase/FoxBase/XBase Database File",
	website : "http://fileformats.archiveteam.org/wiki/DBF",
	ext     : [".dbf"],
	magic   : [/(?:FoxBase\+?\/?)?dBase /, "dBASE Database", /^xBase .*DBF/],
	unsafe  : true
};

exports.steps = [() => ({program : "unoconv", flags : {unoconvType : "csv"}})];
