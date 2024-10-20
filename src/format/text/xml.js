import {Format} from "../../Format.js";

const _XML_MAGIC = [
	// generic XML
	"Extensible Markup Language", "Generic XML", "broken XML document", /^XML .*document/, "XML Datei", "XML Property List", "XML Schema", "application/xml", /^fmt\/101( |$)/, /^x-fmt\/280( |$)/,
	
	// specific XML	(NOTE: I could make a 'format/xmlFiles.js' that has each of these as it's own magic, but I would want to ensure that it's actually XML then by verifying it's valid xml)
	"VCDImager Video CD description", "Windows Manifest - Visual Stylesheet XML file", "Portable Application Description (PAD)", "Apple Interface Builder NIB archive (XML)", "macOS Website Location", "Interface Builder UI resource data (object)",
	"Compass and Ruler geometry", "RSS web feed", "Microsoft .NET XML Resource template", "MSBuild Targets", "Logiqx XML Format", "Glyph Interchange Format", "Web Services Description Language", "Fontconfig Configuration", "Visual Studio .NET Visual C Project",
	"Visual Studio Project User Options", "Visual Studio C++ project Filters", "Visual Studio Visual C++ Project", "JavaHelp TOC", "JBuilder Project", "JavaHelp map", "Wireless Markup Language", "NetBeans project Attributes", "Xcode Scheme",
	"Tag Library Descriptor", "Channel Definition Format", "QuickTime Media Link", "Interface Builder UI resource data (archive)", "Mozilla XML User interface Language", "GPS eXchange format", "Glade UI design", "Internet Archive book scan data",
	"RoboHelp / FlashHelp skin", "Entity and Attribute Information", "Shapefile Geospatial metadata", "NuGet Specification", "Microsoft Management Console Snap-in control file", "Microsoft Extensible Application Markup Language", "XSI Addon",
	"Native Instruments Battery drumKit", "Dia shape", "Dia sheet", "Dia drawing (uncompressed)", "RELAX NG", "XSL Formatting Objects", "DISCO Dynamic Discovery file", "XML sitemap", "GNUMERIC spreedshet (XML", "Open Source Metadata Framework",
	"Outline Processor Markup Language", "application/atom+xml", "application/xslt+xml", "AppleScript Terminology", "application/x-dia-shape", "application/x-gnumeric", "application/x-dia-diagram", "text/x-opml+xml", "C++ Builder XML Project",
	"Death Village stage data", "Atom web feed", "SOAP message", "Lazarus Project Information", "XML Localization Interchange File Format", "application/xliff+xml", "application/rss+xml", "Windows Update Package", "Xcode project data",
	"application/x-glade", "Open Office XML Relationships", "Visual Studio C# Project", "Visual Studio Visual Basic Project", "Game Definition File", "Windows Composite Font", "WCF Configuration Snapshot", "Saved WCF Configuration Information",
	"Maven Project Object Model", "Visual Studio Settings", "ADO.NET Conceptual Schema Definition Language", "ADO.NET Store Schema Definition Language", "Entity Data Model", "VisualStudio MyApp", "JetBrains solution Settings", "LandXML",
	"Java Flight Recorder event settings", "DISCO Discovery Document", "DISCO Discovery Output", "Windows Installer XML Source", "OS X system data", "HRC Language", "Far settings", "Mozilla blocklist", "JAXB Bindings", "ClickOnce Deployment Manifest",
	/^Tiled Tiles (Map|Set) XML$/, "Additive Manufacturing Format", "Microsoft Windows library description", "Microsoft Vista Saved Search", "Windows Mail Account", "Windows Contact", "OS X Flat Package Packageinfo", "OS X Installer GUI script",
	"Continuous Media Markup Language", "GraphML graph", "Kate language syntax", "Class Diagram", "SQL Server Reporting Services Report Definition Language", "JasperReports JRXML report definition", "Borland Developer Studio Project",
	"application/x-xbel", "Windows Script Component", "WiX Localization", "Android compiled View resource", "Scripting Definition", "Xcode Workspace Data", "Android Manifest", "Interface Builder Storyboard document", "RealProducer Profile",
	"Visual Studio Shared Code project", "iOS App Zip archive data", "Open Virtualization Format descriptor", "Borland Group Project", "FastReport 3 report", "XML Bookmark Exchange Language", "ttx font format", "Eclipse Extension Point Schema",
	"ArgoUML project", "Precision Graphics Markup Language", "XML Metadata Interchange", "Thrustmaster TARGET profile", "Java Web Start application descriptor", "MAME Layout", "Distribution Format Exchange Profile", "Artweaver Brush", "IFC-XML",
	"MeshMixer Part data", "Software Ideas Modeler Template", "Navigation Control file for XML", "OpenOffice/LibreOffice type library database (XML)", "OpenCV XML storage", "Mono Mconfig configuration", "Uniform Office Format (generic)",
	"Fabmetheus model format", "Qt Help Collection Project", "MusicXML", "SOAP Envelope", "Windows 7 Task Scheduler job", "GnuCash data", "GnuCash file", "AlgoBox Algorithm", "Visual Studio Tools for Office add-in", "Anjuta IDE project",
	"ConvertXtoDVD project", "Eclipse CDT Project settings", "Koda Form Designer Form",
	/^fmt\/(205|475|896|979|983|986|1219|1474|1677|1729|1776|1796)( |$)/
];
export {_XML_MAGIC};

export class xml extends Format
{
	name           = "Extensible Markup Language";
	website        = "http://fileformats.archiveteam.org/wiki/XML";
	ext            = [".xml"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.LOW;
	mimeType       = "application/xml";
	magic          = _XML_MAGIC;
	weakMagic      = ["Java Web Start application descriptor"];
	untouched      = true;
	metaProvider   = ["text"];
}
