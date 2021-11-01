"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Microsoft Windows Animated Cursor",
	website  : "http://fileformats.archiveteam.org/wiki/ANI",
	ext      : [".ani"],
	mimeType : "application/x-navi-animation",
	magic    : ["Windows Animated Cursor", /^RIFF .* animated cursor$/]
};

exports.converterPriority = [{program : "deark", flags : {dearkKeepAsGIF : true, dearkJoinFrames : true}}];
