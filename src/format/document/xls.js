import {Format} from "../../Format.js";

export class xls extends Format
{
	name       = "Excel Spreadsheet";
	website    = "http://fileformats.archiveteam.org/wiki/XLS";
	ext        = [".xls", ".xlsx", ".xlw", ".xlsm"];
	magic      = [
		"Microsoft Excel worksheet", "Microsoft Excel for OS/2 worksheet", "Microsoft Excel sheet", "Excel Microsoft Office Open XML Format document", "Microsoft Excel for Mac", "CDFV2 Microsoft Excel", /^OLE 2 Compound Document.*Excel 97-2003/,
		"Excel Binary workbook",
		/^Microsoft Office XML Flat File Format Excel worksheet/, /^fmt\/(55|56|57|58|59|61|62|214|445|555|556|598)( |$)/, /^x-fmt\/17( |$)/,

		"Visual Tools Spreadsheet"	// this is actually a sperate format, but only ever encountered one of these and it also matches against excel magics, so just stick it in here since these converters seem to handle it ok
	];
	weakMagic  = ["Microsoft Excel sheet", "Microsoft Excel worksheet (generic older format)"];	// see poly/solidWorksDrawing/kloub.SLDDRW
	idMeta     = ({macFileType, macFileCreator}) => ["sLC3", "sLM3", "sLS3", "XLA ", "XLA5", "XLA8", "XLC3", "XLM ", "XLM3", "XLS ", "XLS3", "XLS4", "XLS5", "XLS8", "XLW4"].includes(macFileType) && macFileCreator==="XCEL";
	converters = [
		"soffice[format:MS Excel 2003 XML]", "soffice[format:MS Excel 97]", "soffice[format:MS Excel 95]", "soffice[format:MS Excel 5.0/95]", "soffice[format:MS Excel 4.0]", "excel97[matchType:magic]",
	
		// Mac files don't appear to be openable very easily by anything else and since soffice without a module specified will open any garbage, skip it
		"soffice[strongMatch][forbiddenMagic:Microsoft Excel for Mac]",
		
		"antixls[strongMatch]"
	];
}
