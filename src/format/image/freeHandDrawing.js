"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "FreeHand Drawing",
	ext   : [".fh", ".fh2", ".fh3", ".fh4", ".fh5", ".fh6", ".fh7", ".fh8", ".fh9"],
	magic : ["FreeHand drawing"]
};

exports.converterPriority = [{program : "soffice", flags : {sofficeType : "svg"}}, "scribus"];
