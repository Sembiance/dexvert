import {Format} from "../../Format.js";

export class lotusWordPro extends Format
{
	name       = "Lotus Word Pro";
	website    = "http://fileformats.archiveteam.org/wiki/Lotus_Word_Pro";
	ext        = [".lwp"];
	magic      = ["Lotus Word Pro document", "Lotus WordPro", "application/vnd.lotus-wordpro", /^fmt\/340( |$)/, /^x-fmt\/340( |$)/];	// yup, both fmt and x-fmt are #340
	converters = ["keyViewPro[outType:pdf]"];
}
