"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "AOL ART Compressed Image",
	website : "http://fileformats.archiveteam.org/wiki/ART_(AOL_compressed_image)",
	ext     : [".art"],
	magic   : ["AOL ART image", "AOL ART (Johnson-Grace compressed) bitmap"]
};

exports.converterPriority = ["graphicWorkshopProfessional"];
