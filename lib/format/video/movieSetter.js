"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MovieSetter Video",
	website : "http://fileformats.archiveteam.org/wiki/MovieSetter",
	ext     : [".avi"],
	magic   : ["MovieSetter project"],
	notes   : XU.trim`
		Xanim doesn't play sound and my runUtil.recordVirtualX also doesn't record sound
		Couldn't find another linux based converter that supports sound. Only known solution now would be to convert it on a virtual amiga with MovieSetter itself probably.`
};

exports.steps = [() => ({program : "xanim"})];
