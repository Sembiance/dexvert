"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "libgd GD Image",
	website     : "https://libgd.github.io/manuals/2.3.0/files/gd_gd-c.html",
	ext         : [".gd"],
	unsafe : true
};

exports.converterPriority = ["gdtopng"];
