"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "GX1 Bitmap",
	website          : "http://fileformats.archiveteam.org/wiki/GX1",
	ext              : [".gx1"],
	magic            : ["GX1 bitmap"],
	unsupported      : true,
	unsupportedNotes : XU.trim`
		Loadable by the DOS version of "Microsoft Paintbrush 2.0" which can be run here: C:\PBRUSH2\PAINT.BAT
		But it doesn't support keyboard shortcuts, so to convert and save as PCX it's all via the menus.
		I don't have mouse support yet for dosUtil, so skipping this for now.`
};
