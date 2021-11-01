"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Abyss Highest Experience Module",
	website : "http://fileformats.archiveteam.org/wiki/AHX_(Abyss)",
	ext     : [".ahx"],
	magic   : [/^AHX .*module data/, "Abyss' Highest eXperience module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123", "zxtune123"];
