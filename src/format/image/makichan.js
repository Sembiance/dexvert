"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MAKIchan Graphic",
	website : "http://fileformats.archiveteam.org/wiki/MAKIchan_Graphics",
	ext     : [".mag", ".max", ".mki"],
	magic   : [/^MAKI v1-[ab] bitmap$/, "MAG v2 bitmap"]
};

exports.converterPriority = ["recoil2png"];
