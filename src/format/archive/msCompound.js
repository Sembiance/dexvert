import {Format} from "../../Format.js";

export class msCompound extends Format
{
	name             = "Microsoft Compound Document";
	website          = "http://fileformats.archiveteam.org/wiki/Microsoft_Compound_File";
	magic            = ["Generic OLE2 / Multistream Compound", "Composite Document File V2 Document", "OLE2 Compound Document Format"];
	forbiddenExt     = [".fpx"];	// Allow image/fpx to handle these
	confidenceAdjust = (input, matchType, curConfidence) => -(curConfidence-40);	// MS Word/Excel files and Thumbs.db are also Compound Documents. Usually archive/* goes first, but let's reduce confidence here so others can go first instead like document/wordDoc
	converters       = ["sevenZip", "unar", "deark[module:cfb][opt:cfb:extractstreams]"];
}
