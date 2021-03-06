"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

// txtByFilename handles files with specific filenames that are likely text but have non-ascii characters which requires loosened magic match of /^data$/
exports.meta =
{
	name      : "Text File",
	website   : "http://fileformats.archiveteam.org/wiki/Text",
	magic     : [...C.TEXT_MAGIC, /^data$/],
	weakMagic : true,
	priority  : C.PRIORITY.VERYLOW,
	filename  :
	[
		/registra.tio/i, /register.*/i,
		/descript.ion/i,
		/file_id.*\.diz/i,
		/^disk_ord.er.?$/i, /ordrform/i,
		/^(about|change|copying|description|manifest|manual|order|problems|readme|readnow|readthis|release|todo|whatsnew)[._-]*($|\..+$)/i,
		/^.*read\..*me.*$/i, /^.*read.*me.*\./i, /^.*read.?me.?$/i, /^read.*me.*$/i, /^.read_this/i, /^whats\.new$/i,
		/^.*manu.al$/i,
		/[_-]te?xt$/i
	],
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
