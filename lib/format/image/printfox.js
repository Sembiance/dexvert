"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name       : "Printfox/Pagefox Bitmap",
	website    : "http://fileformats.archiveteam.org/wiki/Printfox_bitmap",
	ext        : [".gb", ".bs", ".pg", ".bin"],
	// .bin doesn't convert correctly with nconvert, so if we detect it in a filename like shark.gb.bin then we check to see if .gb is a valid ext, otherwise we just use .gb
	safeExt    : state => (state.input.ext.toLowerCase()===".bin" ? (exports.meta.ext.find(v => v===path.extname(state.input.name).toLowerCase()) || ".gb") : state.input.ext.toLowerCase()),
	magic      : ["PrintFox/Pagefox bitmap"],
	weakMagic  : true,
	trustMagic : true
};

exports.converterPriorty = ["nconvert"];
