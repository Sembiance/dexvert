"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "Microsoft Windows Animated Cursor",
	website          : "http://fileformats.archiveteam.org/wiki/ANI",
	ext              : [".ani"],
	mimeType         : "application/x-navi-animation",
	magic            : ["Windows Animated Cursor", /^RIFF .* animated cursor$/]
};

exports.preSteps = [state => { state.dearkJoinFrames = true; }];
exports.converterPriorty = ["deark"];
exports.postSteps = [state => { delete state.dearkJoinFrames; }];
