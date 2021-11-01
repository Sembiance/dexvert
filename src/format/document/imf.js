/*
import {Format} from "../../Format.js";

export class imf extends Format
{
	name = "Internet Message Format";
	website = "http://fileformats.archiveteam.org/wiki/Internet_e-mail_message_format";
	ext = [".eml",".msg"];
	magic = ["E-Mail message","news or mail","news, ASCII text"];
	unsupported = true;
	notes = "\nWith several RFC files describing the format, uou'd think this would be straight forward to parse, but it's a total nightmare.\nI had spent some time looking for a good program to parse it, and failed.\nI spent more time trying to code my own that would output JSON, but there are just a ton of edge cases and I gave up.\nIn addition to the website link above, more details here: https://mailformat.dan.info/";
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Internet Message Format",
	website     : "http://fileformats.archiveteam.org/wiki/Internet_e-mail_message_format",
	ext         : [".eml", ".msg"],
	magic       : ["E-Mail message", "news or mail", "news, ASCII text"],
	unsupported : true,
	notes       : XU.trim`
		With several RFC files describing the format, uou'd think this would be straight forward to parse, but it's a total nightmare.
		I had spent some time looking for a good program to parse it, and failed.
		I spent more time trying to code my own that would output JSON, but there are just a ton of edge cases and I gave up.
		In addition to the website link above, more details here: https://mailformat.dan.info/`
};

*/
