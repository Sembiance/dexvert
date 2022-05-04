import {Format} from "../../Format.js";

export class lotusWordPro extends Format
{
	name        = "Lotus Word Pro";
	website     = "http://fileformats.archiveteam.org/wiki/Lotus_Word_Pro";
	ext         = [".lwp"];
	magic       = ["Lotus Word Pro document", "Lotus WordPro", /^fmt\/340( |$)/];
	unsupported = true;
}
