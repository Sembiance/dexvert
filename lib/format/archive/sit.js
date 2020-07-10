"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Stuffit Archive",
	ext      : [".sit"],
	magic    : ["StuffIt compressed archive", /StuffIt Archive/],
	program  : "unar"
};
