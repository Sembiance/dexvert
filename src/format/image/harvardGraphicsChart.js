import {Format} from "../../Format.js";

export class harvardGraphicsChart extends Format
{
	name       = "Harvard Graphics Chart";
	website    = "http://fileformats.archiveteam.org/wiki/Harvard_Graphics";
	ext        = [".ch3", ".sy3", ".cht", ".tp3"];
	magic      = ["Harvard Graphics Chart", /^x-fmt\/(32|325)( |$)/];
	converters = ["canvas[matchType:magic][nonRaster]"];
}
