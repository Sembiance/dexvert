"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "DataShow Sound File",
	website     : "http://www.amateur-invest.com/us_datashow.htm",
	ext         : [".snd"],
	magic       : ["DataShow sounds/music"],
	weakMagic   : true,
	unsupported : true,
	notes       : "The single sample file I have is a simple text file on how to generate the sound. Probably wouldn't be too hard to create a converter for it. But it's a pretty obscure format, so probably not worth investing any time into it."
};
