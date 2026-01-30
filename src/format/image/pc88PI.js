import {Format} from "../../Format.js";

export class pc88PI extends Format
{
	name       = "NEC PC-88 PI";
	website    = "http://fileformats.archiveteam.org/wiki/Pi_(image_format)";
	ext        = [".pi"];
	magic      = ["Pi bitmap", "Yanagisawa Pi 16 color picture"];
	idMeta      = ({macFileType, macFileCreator}) => macFileType==="__PI" && macFileCreator==="xPIC";
	converters = ["recoil2png", "wuimg[format:pi]"];
}
