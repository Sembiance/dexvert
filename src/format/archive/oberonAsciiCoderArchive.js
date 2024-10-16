import {Format} from "../../Format.js";

export class oberonAsciiCoderArchive extends Format
{
	name       = "Oberon AsciiCoder archive";
	website    = "https://web.archive.org/web/20170312142117/http://www.ethoberon.ethz.ch/ethoberon/tutorial/Compress.html";
	magic      = ["Oberon V4 AsciiCoder archive"];
	converters = ["asciidecoder"];
}
