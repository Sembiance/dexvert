"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Mac PageMill's GIF Bitmap",
	ext            : [".gif"],
	forbidExtMatch : true,
	magic          : ["Mac PageMill's GIF bitmap"]
};

exports.converterPriority = ["graphicWorkshopProfessional", "imageAlchemy"];
