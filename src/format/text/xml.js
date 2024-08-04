import {Format} from "../../Format.js";

const _XML_MAGIC = [
	// generic XML
	"Extensible Markup Language", "Generic XML", "broken XML document", /^XML .*document/, "XML Datei", "XML Property List", "XML Schema", /^fmt\/101( |$)/, /^x-fmt\/280( |$)/,
	
	// specific XML
	"VCDImager Video CD description", "Windows Manifest - Visual Stylesheet XML file", "Portable Application Description (PAD)", "Apple Interface Builder NIB archive (XML)", "macOS Website Location", "Interface Builder UI resource data (object)",
	"Compass and Ruler geometry", "RSS web feed", "Microsoft .NET XML Resource template", "MSBuild Targets", "Logiqx XML Format", "Glyph Interchange Format", "Web Services Description Language",
	/^fmt\/(979|983|1677)( |$)/
];
export {_XML_MAGIC};

export class xml extends Format
{
	name           = "Extensible Markup Language";
	website        = "http://fileformats.archiveteam.org/wiki/XML";
	ext            = [".xml"];
	forbidExtMatch = true;
	mimeType       = "application/xml";
	magic          = _XML_MAGIC;
	untouched      = true;
	metaProvider   = ["text"];
}
