"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "X11 Pixmap",
	website  : "http://fileformats.archiveteam.org/wiki/XPM",
	ext      : [".xpm", ".pm"],
	mimeType : "image/x-xpixmap",
	magic    : ["X PixMap bitmap", "X-Windows Pixmap Image", "X pixmap image"]
};

exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
