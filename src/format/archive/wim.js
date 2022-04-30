import {Format} from "../../Format.js";

export class wim extends Format
{
	name       = "Windows Imaging Format";
	website    = "http://fileformats.archiveteam.org/wiki/WIM";
	ext        = [".wim", ".swm", ".esd", ".wim2", ".ppkg"];
	magic      = [/^Windows [iI]maging/];
	converters = ["wimapply", "sevenZip", "UniExtract"];
}
