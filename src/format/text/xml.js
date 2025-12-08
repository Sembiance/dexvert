import {Format} from "../../Format.js";

const _XML_MAGIC = [
	// generic XML
	"Extensible Markup Language", "Generic XML", "broken XML document", /^XML .*document/, "XML Datei", "XML Property List", "XML Schema", "application/xml", /^fmt\/101( |$)/, /^x-fmt\/280( |$)/,
	
	// specific XML	(NOTE: I could make a 'format/xmlFiles.js' that has each of these as it's own magic, but I would want to ensure that it's actually XML then by verifying it's valid xml)
	// Also, some of these could be processed into something more usable, such as'Photo Font' etc.
	"VCDImager Video CD description", "Windows Manifest - Visual Stylesheet XML file", "Portable Application Description (PAD)", "Apple Interface Builder NIB archive (XML)", "macOS Website Location", "Interface Builder UI resource data (object)",
	"Compass and Ruler geometry", "RSS web feed", "Microsoft .NET XML Resource template", "MSBuild Targets", "Logiqx XML Format", "Glyph Interchange Format", "Web Services Description Language", "Fontconfig Configuration", "Eclipse JAR settings",
	"Visual Studio Project User Options", "Visual Studio C++ project Filters", "Visual Studio Visual C++ Project", "JavaHelp TOC", "JBuilder Project", "JavaHelp map", "Wireless Markup Language", "NetBeans project Attributes", "Xcode Scheme",
	"Tag Library Descriptor", "Channel Definition Format", "QuickTime Media Link", "Interface Builder UI resource data (archive)", "Mozilla XML User interface Language", "GPS eXchange format", "Glade UI design", "Internet Archive book scan data",
	"RoboHelp / FlashHelp skin", "Entity and Attribute Information", "Shapefile Geospatial metadata", "NuGet Specification", "Microsoft Management Console Snap-in control file", "Microsoft Extensible Application Markup Language", "XSI Addon",
	"Native Instruments Battery drumKit", "Dia shape", "Dia sheet", "Dia drawing (uncompressed)", "RELAX NG", "XSL Formatting Objects", "DISCO Dynamic Discovery file", "XML sitemap", "GNUMERIC spreedshet (XML", "Open Source Metadata Framework",
	"Outline Processor Markup Language", "application/atom+xml", "application/xslt+xml", "AppleScript Terminology", "application/x-dia-shape", "application/x-gnumeric", "application/x-dia-diagram", "text/x-opml+xml", "C++ Builder XML Project",
	"Death Village stage data", "Atom web feed", "SOAP message", "Lazarus Project Information", "XML Localization Interchange File Format", "application/xliff+xml", "application/rss+xml", "Windows Update Package", "Xcode project data", "TEI document",
	"application/x-glade", "Open Office XML Relationships", "Visual Studio C# Project", "Visual Studio Visual Basic Project", "Game Definition File", "Windows Composite Font", "WCF Configuration Snapshot", "Saved WCF Configuration Information",
	"Maven Project Object Model", "Visual Studio Settings", "ADO.NET Conceptual Schema Definition Language", "ADO.NET Store Schema Definition Language", "Entity Data Model", "VisualStudio MyApp", "JetBrains solution Settings", "LandXML",
	"Java Flight Recorder event settings", "DISCO Discovery Document", "DISCO Discovery Output", "Windows Installer XML Source", "OS X system data", "HRC Language", "Far settings", "Mozilla blocklist", "JAXB Bindings", "ClickOnce Deployment Manifest",
	/^Tiled Tiles (Map|Set) XML$/, "Additive Manufacturing Format", "Microsoft Windows library description", "Microsoft Vista Saved Search", "Windows Mail Account", "Windows Contact", "OS X Flat Package Packageinfo", "OS X Installer GUI script",
	"Continuous Media Markup Language", "GraphML graph", "Kate language syntax", "Class Diagram", "SQL Server Reporting Services Report Definition Language", "JasperReports JRXML report definition", "Borland Developer Studio Project", "Pencil sketch",
	"application/x-xbel", "Windows Script Component", "WiX Localization", "Android compiled View resource", "Scripting Definition", "Xcode Workspace Data", "Android Manifest", "Interface Builder Storyboard document", "RealProducer Profile",
	"Visual Studio Shared Code project", "iOS App Zip archive data", "Open Virtualization Format descriptor", "Borland Group Project", "FastReport 3 report", "XML Bookmark Exchange Language", "ttx font format", "Eclipse Extension Point Schema",
	"ArgoUML project", "Precision Graphics Markup Language", "XML Metadata Interchange", "Thrustmaster TARGET profile", "Java Web Start application descriptor", "MAME Layout", "Distribution Format Exchange Profile", "Artweaver Brush", "IFC-XML",
	"MeshMixer Part data", "Software Ideas Modeler Template", "Navigation Control file for XML", "OpenOffice/LibreOffice type library database (XML)", "OpenCV XML storage", "Mono Mconfig configuration", "Uniform Office Format (generic)",
	"Fabmetheus model format", "Qt Help Collection Project", "MusicXML", "SOAP Envelope", "Windows 7 Task Scheduler job", "GnuCash data", "GnuCash file", "AlgoBox Algorithm", "Visual Studio Tools for Office add-in", "Anjuta IDE project", "ISE XReport",
	"ConvertXtoDVD project", "Eclipse CDT Project settings", "Koda Form Designer Form", "Synfig project", /^Delphi Project$/, "Notepad++ session", "wxFormBuilder Project", "Scribus palette", "FET Timetable", "LMMS Preset", "LMMS Project", "SWID Tag",
	"Microsoft security certificate", "Expression Design swatch (v4)", "Microsoft security certificate", "GanttProject project", "SMath Studio worksheet", "MuseScore music score", "NewsML file", "DcUpdater local configuration", "WxGlade project",
	"Group Policy Administrative Template", "Group Policy Language-Specific Administrative Template", "Mixxx MIDI preset", "TreeDBNotes syntax config", "application/vnd.kde.kcfg", "Mixxx controller preset", "Code::Blocks Project", "QTI document",
	"MAME ListXML format", "AutoCAD drawing lock", "EDraw Max drawing", "Citation Style Language", "Friend of a Friend (FOAF) Resource Description Framework", "Gnumeric spreadsheet", "OEB Package Format eBook", "Find and Run Robot (FARR) alias",
	"Kingsoft Antivirus component install info", "PC AntiVirus Virus DB collection info", "KDevelop Session", "Final Cut Pro XML Interchange Format", "Zilog Developer Studio II Target", "Zilog Developer Studio II Project", "mzXML format",
	"XML BLAST Output", "Windows Search Connector", "Bayesian Networks Interchange Format", "Geography Markup Language", "Ivy module descriptor", "LEGO Digital Designer XML data", "SQL Server Integration Services package", "KWordQuiz learning file",
	/^uVision v[245] Project( Options)?/, "CMSIS System View Description format", /^IAR Embedded Workbench (Project|Workspace)/, "GDAL Virtual Format (vector)", /^Programmer's Notepad (Scheme|text Clips|user preset)/, "Adobe Premiere Title",
	"IAR Embedded Workbench Debug info", "Xilinx ISE Messages", "Visual Studio .NET Visual C Project", "VMware supplemental team member configuration", "Microsoft Visual Studio project template", "PRONOM file format report", "Flex configuration",
	"Windows application Manifest", "OSTA.org MusicPhotoVideo", "BlackBerry Application Loader", "Viewpoint MetaStream scene", "FlashDevelop ActionScript 3 Project", "Windows application Manifest (generic)", "Morpheus layout - project", "XML Grammar",
	"Wink Flash Preloader", "Wink Flash Control bar", "MAME Hash", "openMSX machine/device configuration", "ActiveReports Report (UTF-8)", "Papyrus X DB XML", /^VOTable$/, "Audacity Project", "XML Shareable Playlist Format", "application/xspf+xml",
	"application/x-quicktime-media-link", /^Metalink \([^)]+\)$/, "NVDL script", ".NET assembly uninstaller info", "ArcPad configuration", "Predictive Model Markup Language", "SecurID Soft Token", "Qt Assistant Documentation Profile", "Karma Workspace",
	"Microsoft Project Data Interchange XML format", "Papyrus X report XML", /^TextMate (Command|Language grammar|Theme)$/, "Apple Keynote Presentation data", "Microsoft SQL Server Analysis Services Project", "Windows PowerShell formatting (UTF-8)",
	"psitree router configuration", "Rosegarden score (ungzipped)", "Bitz and Pixels XML", "CAPS metadata", "KRadio Preset", "ActiveReports Report", "Help Table of Contents", "Hex Edit binary file format template", "Google Desktop Gadget manifest",
	"XAML Browser Applications", "Windows PowerShell types", "Borland user specific project options", "ISE Project generated data", "Altera Qsys System", "Xilinx ISE Project", "Code::Blocks Workspace Layout", "Kettle Transformation", "Planner project",
	"Portable Application Description (UTF-8) (PAD)", "Siemens TIA project (v11)", "DockPanel configuration", "GObject Introspection information", "application/metalink+xml", "ZModeler profile", "Compass and Ruler Macro", "Softimage Scene TOC",
	"Vikon Skeleton template", "Chemical Markup Language XML document", "m0n0wall configuration", "MLT XML document", "Jahshaka Scene File", "ksudoku puzzle", /^Linden (avatar|skeleton) definition/, "RealProducer Job File", "Google Earth network link",
	/^Visual Studio J# Project \(v[78]\)$/, "Visual Studio JavaScript Project", "UniHighlighter Highlighter definition", "BORGChat configuration", "BORGChat smiles", "Zope Configuration Mark-up Language", "application/x-drgeo", "Hydrogen Song",
	/^Together Class Diagram \(UML [\d.]+\)/, "Liberty BASIC Lesson", "Teach2000 document", "AutoCAD Color Book", "Crytek XML Material", "FMOD Designer Project", "XML Forms Data Format", "Adobe Premiere Effect Preset", "QuarkXPress Color Library",
	"Mac OS installable Keyboard Layout", "QuarkXPress Color Library UI specs", "Nmap scan results (XML)", "PAM Dataset", "Havok XML format", "Maple XML Worksheet", "Okteta grammar (XML)", "Code::Blocks wxSmith resource", "PyDev Project", "Photo Font",
	"Sandcastle Help File Builder Project", "Battlefield 2 mod Description", "Visual Studio Publish profile", "Qt Help Project", "RoboHelp XML Project", "Rosegarden note style", "TextMate Preferences", "TextMate Project", "OmniOutliner document",
	"SMath Studio document (old)", "XBMC Smart Playlist", "Abstract Markup Language", "WiX Project (UTF-8)", "Code::Blocks lexer", "UpdateStar info", "Lazarus Package", "Code::Blocks lexer", "KlipFolio Klip", "XMLTV format", "NewsML", "WiX Library",
	"RAD Studio modeling Configuration", "Code::Blocks Workspace", "WiX Object", "Filter Forge filter", "Microsoft Flight Simulator Flight Plan", "gretl Data", "MzXML mass spectrometer output data", "Poseidon for UML Project information", "ChemDraw XML",
	"Garmin Training Center Database XML", "Cal3D Xml Skeleton File", "Apple Quartz Filter", "Torque sprite asset (XML)", "ImmerVision XML user interface", "Amnesia: T.D.D. sound entity", "Instant3D document", "Microsoft Assistance Markup Language (UTF-8)",
	"DialogBlocks Project", /^FinalBuilder (actions Package|code completion info|Project \(v4\)|Wizard)/, "Adobe Premiere Preset", "Automise Project (v3)", "OWL XML Ontology", /^Gentoo (category|package) metadata file/, "Newzbin Usenet Index",
	"MiSTer Game Launcher", "XML Data Package", "SPSS Analysis Plan", "SPSS Sampling Plan", "DeleD scene", "Net2Plan Network design", "MAME software list", "Mathcad XML based worksheet", /^PowerDesigner (Conceptual )?(Model|WorkSpace)$/,
	"SQL Server Data Tools Database info", "Visual Studio Intel Fortran Project", "VideoWave Movie Project", "Visual Studio Data Source", "Autodesk Inventor Project", "FxCop project", "EtherPeek/AiroPeek/OmniPeek capture file", /^DITA (Map|structure)/,
	"Eclipse Launch configuration", "Amazing Mahjongg 3D Layout", "TermBase eXchange Format", "Translation Memory Exchange", "GENPO Organ", "GNOME Timed Wallpaper", "JavaServer FacesServlet pointer", "VSIX Manifest (2010)",
	/^fmt\/(205|243|333|475|570|896|932|979|982|983|986|1134|1219|1357|1463|1474|1613|1677|1729|1776|1796|1824|1825|1883|1962|2032|2033|2034)( |$)/, /^x-fmt\/227( |$)/
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
	untouched      = true;
	metaProvider   = ["text"];
}
