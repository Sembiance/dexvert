import {Format} from "../../Format.js";

export class msCompound extends Format
{
	name             = "Microsoft Compound Document";
	website          = "http://fileformats.archiveteam.org/wiki/Microsoft_Compound_File";
	magic            = [
		// generic msCompound
		"Generic OLE2 / Multistream Compound", "Composite Document File V2 Document", "OLE2 Compound Document Format", "OLE 2 Compound Document", /^CFBF$/,
		
		// app specific: I could look into these more and support them better
		"Shell Scrap object", "StormFront skin", "Ulead PhotoImpact Object(s)", "Designworks Template (v3.5)", "Easy CD Creator's Jewel case", "STATISTICA Workbook", "Ulead iPhoto Template", "iPublish document", "Quattro Pro 7 spreadsheet",
		"Creative Witer document", "3D Studio Max Material Library", "Windows Movie Maker project", "Roxio/MGI PhotoSuite Album", "Roxio/MGI PhotoSuite Project", "Avery DesignPro Label design", "Micrografx Simply 3D project", "Micrografx clipart index",
		"WordPerfect Slide Show", "ArcGIS Map project", "JewelCase Maker project", "Corel Gallery", "Serif PhotoPlus Picture (OLE)", "Neato MediaFACE label template", "EMB Wilcom Design embroidery file", "Melco DesignShop Project", "CDFV2 QuickBooks",
		"Perfect Keyboard macro set", "CorelCAD Drawing", "CorelCAD Drawing Template", "CorelCAD Custom Views", "Corel Flow Smart Library", "MPLAB IDE Workspace", "Crystal Reports output file (Report)", "Minitab Worksheet (V12 1998)", "ArcGIS Layer",
		"Minitab Portable Worksheet", "Windows 7 Jump List", "Microsoft RSS Feeds Store", "Combit List and Label printer setup file", "Visual Pinball Table", "AutoRoute Export file", "Lotus Approach (generic)", "Outlook Send-Receive Settings",
		"MSN Messenger Wink", "Protel for Windows schematic capture (binary)", "Protel PCB 5.0 Binary Library", "Altium Designer PCB Document", "Lotus Approach v3.0", "ACT! Macro (v3.0)", "AutoCAD VBA macro", "Font FX Material", "Font FX Path",
		"Easy CD Creator Layout", "Oracle Data base Diagram", "CeledyDraw drawing", "Microsoft Access Wizard template", "Office Binder Document", "Microsoft Access Project", "ASAP Presentation", "Microsoft Clip Art Gallery Catalog", "Samsung document",
		"Drafix Symbol Library", "WebLab Viewer Molecule", "Camtasia Studio Screen Recording", "Encrypted OLE2 / Multistream Compound File (ECP v1.0)", "Microsoft Visual Studio binary macro project", "Autodesk Inventor Part", "Calendar Creator 5 project",
		"Calendar Creator 5 ClipArt Archive", "OrCAD PSpice Capture Symbols Models", "Autodesk Revit Template", "Revit Family Architecture project", "Diagram Studio Document", "Kingsoft Presentation template", "Orcad Schematic Capture Backup",
		"Rockwell Logix 500 SLC-5 Software", "muvee autoProducer Project", "VideoStudio Project", "DesignCAD drawing", "Font FX Template", "Softimage Scene", "Softimage Exported 3D Model", "Ability Office Spreadsheet", "Intergraph SmartSketch Drawing",
		"Blaze Media Pro Skin",
		/^fmt\/(240|877|916|971|1213|1297|1298|1303|1330|1331|1346|1349|1360|1362|1386|1431|1432|1493|1517|1648|1852|1878)( |$)/, /^x-fmt\/(151|243)( |$)/
	];
	idMeta           = ({macFileType, macFileCreator}) => macFileType==="MSIV" && macFileCreator==="MSIZ";
	forbiddenExt     = [".fpx"];	// Allow image/fpx to handle these
	confidenceAdjust = (input, matchType, curConfidence) => -(curConfidence-40);	// MS Word/Excel files and Thumbs.db are also Compound Documents. Usually archive/* goes first, but let's reduce confidence here so others can go first instead like document/wordDoc
	converters       = ["sevenZip", "unar", "deark[module:cfb][opt:cfb:extractstreams]"];
	notes            = "The app specific msCompound files cound be improved to handle the specific sub-files contained within each type.";
}
