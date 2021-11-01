"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "IBM Storyboard Text Maker Document",
	website        : "https://winworldpc.com/product/ibm-storyboard/",
	ext            : [".txm"],
	forbidExtMatch : true,
	magic          : ["IBM Storyboard screen Capture"], // Identified as a 'screen Capture' but is often a text document, still, we will require the .txm via weakMagic prop
	weakMagic      : true,
	notes          : "Storboard 1.0.1 text maker can open these, but I didn't see any way to convert them to TXT nor 'print' them. So we just use strings which is pretty good at getting the text out."
};

exports.converterPriority = ["strings"];
