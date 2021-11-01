"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "MediaPaq DCF Catalog",
	ext         : [".dcf"],
	magic       : ["DCF images container"],
	unsupported : true,
	notes       : "Metadata and thumbnails archive for MediaClips clip art CDs. NOT related to the DCF camera standard."
};
