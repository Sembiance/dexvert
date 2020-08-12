"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name  : "Print-Technik HIR Image",
	ext   : [".hir"],
	magic : ["Print-Technik/PRO89xx Raw data bitmap"]
};

exports.converterPriorty = ["recoil2png"];
