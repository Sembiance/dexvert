import {Format} from "../../Format.js";

const _XML_MAGIC = [
	// generic XML
	"Extensible Markup Language", "Generic XML", "broken XML document", /^XML .*document/, "XML Datei", "XML Property List", "XML Schema", "application/xml", /^fmt\/101( |$)/, /^x-fmt\/280( |$)/,
	
	// specific XML
	"VCDImager Video CD description", "Windows Manifest - Visual Stylesheet XML file", "Portable Application Description (PAD)", "Apple Interface Builder NIB archive (XML)", "macOS Website Location", "Interface Builder UI resource data (object)",
	"Compass and Ruler geometry", "RSS web feed", "Microsoft .NET XML Resource template", "MSBuild Targets", "Logiqx XML Format", "Glyph Interchange Format", "Web Services Description Language", "Fontconfig Configuration", "Visual Studio .NET Visual C Project",
	"Visual Studio Project User Options", "Visual Studio C++ project Filters (UTF-8)", "Visual Studio Visual C++ Project (UTF-8)", "JavaHelp TOC", "JBuilder Project", "JavaHelp map", "Wireless Markup Language", "NetBeans project Attributes",
	"Tag Library Descriptor", "Channel Definition Format", "QuickTime Media Link", "Interface Builder UI resource data (archive)", "Mozilla XML User interface Language", "GPS eXchange format", "Glade UI design", "Internet Archive book scan data",
	"RoboHelp / FlashHelp skin", "Entity and Attribute Information", "Shapefile Geospatial metadata", "NuGet Specification", "Microsoft Management Console Snap-in control file", "Microsoft Extensible Application Markup Language",
	"Native Instruments Battery drumKit", "Dia shape", "Dia sheet", "Dia drawing (uncompressed)", "RELAX NG", "XSL Formatting Objects", "DISCO Dynamic Discovery file", "XML sitemap", "GNUMERIC spreedshet (XML", "Open Source Metadata Framework",
	"Outline Processor Markup Language", "application/atom+xml", "application/x-designer", "application/xslt+xml", "AppleScript Terminology",
	/^Tiled Tiles (Map|Set) XML$/,
	/^fmt\/(205|475|979|983|1219|1677|1729|1796)( |$)/
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
