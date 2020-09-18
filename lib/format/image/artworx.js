"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name           : "ArtWorx Data Format",
	website        : "http://fileformats.archiveteam.org/wiki/ArtWorx_Data_Format",
	ext            : [".adf"],
	mimeType       : "image/x-artworx",
	magic          : [/^data$/],
	forbiddenMagic : ["Amiga Disk image File", ...C.TEXT_MAGIC],
	weakMagic      : true,
	bruteUnsafe    : true
};

// deark messes up several images, but ansilove seems to handle them all
exports.converterPriorty = [{program : "ansilove", stateFlags : {ansiloveType : "adf"}}, "deark", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.ansiArtInputMeta(state, p, cb);
