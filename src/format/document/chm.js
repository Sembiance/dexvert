import {Format} from "../../Format.js";

export class chm extends Format
{
	name       = "Windows Compiled HTML Help File";
	website    = "http://fileformats.archiveteam.org/wiki/CHM";
	ext        = [".chm"];
	magic      = ["MS Windows HtmlHelp Data", "Windows HELP File", "Microsoft HTML-Hilfe Datei (CHM)", "Format: Microsoft Compiled HTML Help", /^fmt\/634( |$)/];
	weakMagic  = ["Windows HELP File"];
	notes      = "chmdeco and chmdump both failed to process IEXPLORE.CHM and I didn't try any others. FIND.CHM and ACCESSIB_18.CHM fail to extract with archmage.";
	converters = ["archmage", "UniExtract", "ebook_convert"];
}
