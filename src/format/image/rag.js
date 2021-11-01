"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "RAG-D",
	website : "http://fileformats.archiveteam.org/wiki/RAG-D",
	ext     : [".rag"],
	magic   : ["RAG-D bitmap"]
};

exports.converterPriority = ["recoil2png"];
