import {Format} from "../../Format.js";

export class fileMakerPro3 extends Format
{
	name           = "FileMaker Pro 3 Database";
	website        = "http://fileformats.archiveteam.org/wiki/FileMaker_Pro";
	ext            = [".fp3"];
	forbidExtMatch = true;
	magic          = ["FileMaker Pro 3 database"];
	converters     = ["strings"];
}
