"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "HP Palmtop Icon",
	website  : "http://fileformats.archiveteam.org/wiki/HP_100LX/200LX_icon",
	ext      : [".icn", ".xbg"],
	magic    : [/HP Palmtop .*Icon$/]
};

exports.converterPriority = ["deark"];
