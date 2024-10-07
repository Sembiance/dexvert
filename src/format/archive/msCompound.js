import {Format} from "../../Format.js";

export class msCompound extends Format
{
	name             = "Microsoft Compound Document";
	website          = "http://fileformats.archiveteam.org/wiki/Microsoft_Compound_File";
	magic            = [
		// generic msCompound
		"Generic OLE2 / Multistream Compound", "Composite Document File V2 Document", "OLE2 Compound Document Format", "OLE 2 Compound Document", /^CFBF$/,
		
		// app specific: I could look into these more and support these better
		"Shell Scrap object", "StormFront skin", "Ulead PhotoImpact Object(s)", "Designworks Template (v3.5)", "Easy CD Creator's Jewel case", "STATISTICA Workbook", "Ulead iPhoto Template", "iPublish document", "Quattro Pro 7 spreadsheet",
		"Creative Witer document", "3D Studio Max Material Library", "Windows Movie Maker project", "Roxio/MGI PhotoSuite Album", "Roxio/MGI PhotoSuite Project", "Avery DesignPro Label design", "Micrografx Simply 3D project", "Micrografx clipart index",
		"WordPerfect Slide Show", "ArcGIS Map project", "JewelCase Maker project", "Corel Gallery", "Serif PhotoPlus Picture (OLE)", "Neato MediaFACE label template", "EMB Wilcom Design embroidery file", "Melco DesignShop Project",
		"Perfect Keyboard macro set", "CorelCAD Drawing", "CorelCAD Drawing Template", "CorelCAD Custom Views", "Corel Flow Smart Library",
		/^fmt\/(877|916|1213|1303|1360|1648|1878)( |$)/, /^x-fmt\/(151|243)( |$)/
	];
	forbiddenExt     = [".fpx"];	// Allow image/fpx to handle these
	confidenceAdjust = (input, matchType, curConfidence) => -(curConfidence-40);	// MS Word/Excel files and Thumbs.db are also Compound Documents. Usually archive/* goes first, but let's reduce confidence here so others can go first instead like document/wordDoc
	converters       = ["sevenZip", "unar", "deark[module:cfb][opt:cfb:extractstreams]"];
	notes            = "The app specific msCompound files cound be improved to handle the specific sub-files contained within each type.";
}
