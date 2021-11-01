"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "OpenDocument Drawing",
	website   : "http://fileformats.archiveteam.org/wiki/OpenDocument_Drawing",
	ext       : [".odg", ".otg", ".fodg"],
	magic     : ["ZIP Format", "ZIP compressed achive", "Zip archive data"],
	weakMagic : true
};

exports.converterPriority = [{program : "soffice", flags : {sofficeType : "svg"}}];
