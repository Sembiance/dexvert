import {Format} from "../../Format.js";

export class wim extends Format
{
	name       = "Windows Imaging Format";
	website    = "http://fileformats.archiveteam.org/wiki/WIM";
	ext        = [".wim", ".swm", ".esd", ".wim2", ".ppkg"];
	magic      = [/^Windows [iI]maging/, /^fmt\/614( |$)/];
	converters = ["wimapply", "sevenZip", "UniExtract"];
}
