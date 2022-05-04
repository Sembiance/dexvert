import {Format} from "../../Format.js";

export class fileMakerPro extends Format
{
	name           = "FileMaker Pro Database";
	website        = "http://fileformats.archiveteam.org/wiki/FileMaker_Pro";
	ext            = [".fp3"];
	forbidExtMatch = true;
	magic          = ["FileMaker Pro 3 database", "Filemaker Pro (generic)", "FileMaker Pro database", /^x-fmt\/318( |$)/];
	converters     = ["strings"];
}
