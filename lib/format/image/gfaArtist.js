"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "GFA Artist",
	website  : "http://fileformats.archiveteam.org/wiki/GFA_Artist",
	ext      : [".art"],
	mimeType : "image/x-gfa-artist"
};

exports.converterPriorty = ["abydosconvert"];
