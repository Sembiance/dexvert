"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "TTW Compressed File",
	website          : "http://fileformats.archiveteam.org/wiki/TTW",
	ext              : [".cr"],
	magic            : ["TTW Compressed File"],
	unsupported      : true,
	unsupportedNotes : XU.trim`
		Amiga xfdmaster can supposedly decrunch this. 'vamos' won't run it right.
		Could emulate an amiga to support this. htpps://aminet.net/package/util/pack/xfdmaster`
};
