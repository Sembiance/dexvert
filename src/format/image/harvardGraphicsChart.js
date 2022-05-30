import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class harvardGraphicsChart extends Format
{
	name           = "Harvard Graphics Chart";
	website        = "http://fileformats.archiveteam.org/wiki/Harvard_Graphics";
	ext            = [".ch3", ".sy3", ".cht", ".tp3"];
	magic          = ["Harvard Graphics Chart", /^x-fmt\/(32|325)( |$)/];
	weakMagic      = [/^x-fmt\/325( |$)/];
	forbiddenMagic = TEXT_MAGIC;
	converters     = ["canvas[matchType:magic][nonRaster]"];
}
