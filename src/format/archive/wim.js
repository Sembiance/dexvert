import {Format} from "../../Format.js";

export class wim extends Format
{
	name       = "Windows Imaging Format";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_Imaging_Format";
	ext        = [".wim", ".swm", ".esd", ".wim2", ".ppkg"];
	magic      = ["Archive: Windows Imaging Format", /^Windows [iI]maging/, /^fmt\/614( |$)/];
	converters = ["wimapply", "sevenZip[matchType:magic]", "UniExtract[matchType:magic]"];
}
