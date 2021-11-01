"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Ventura Publisher Graphic",
	website     : "http://fileformats.archiveteam.org/wiki/Ventura_Publisher",
	ext         : [".vgr"],
	magic       : ["Ventura Publisher Graphics bitmap"],
	unsupported : true,
	notes       : "Tried both Ventura Publisher 4.1 and Corel Draw 5 (which includes it) and neither could open the sample VGR files I have."
};
