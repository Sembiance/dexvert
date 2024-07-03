import {TEXT_MAGIC} from "../Detection.js";

// All of the formats in this file are 'text' files that should just be handled as text
// Each entry also has the following properties added:
//	forbidExtMatch : true			(Only if ext is set AND we have magic)
//	untouched      : true
//	metaProvider   : ["text"]

export default
{
	text :
	{
		amigaDOSScript                    : {name : "AmigaDOS Script File", website : "https://amigasourcecodepreservation.gitlab.io/mastering-amigados-scripts/", magic : ["AmigaDOS script"]},
		amosSource                        : {name : "AMOS Source Code", ext : [".amossourcecode"]},
		asm                               : {name : "Assembly Source File", website : "http://fileformats.archiveteam.org/wiki/Assembly_language", ext : [".asm"], magic : [...TEXT_MAGIC, "C source"], weakMagic : true},
		bas                               : {name : "BASIC Source File", website : "http://fileformats.archiveteam.org/wiki/BASIC", ext : [".bas"], magic : TEXT_MAGIC, weakMagic : true},
		batDOS                            : {name : "DOS Batch File", website : "http://fileformats.archiveteam.org/wiki/Batch_file", ext : [".bat"], magic : ["DOS batch file", "BAT/CMD Batch Datei", ...TEXT_MAGIC, /^data$/], weakMagic : true},
		batMenuConfiguration              : {name : "BatMenu configuration", ext : [".mnu"], magic : ["BatMenu configuration"]},
		brikChecksums                     : {name : "Brik checksums", magic : ["Brik checksums"]},
		chemicalMoleculeData              : {name : "CHEMICAL molecule Data", ext : [".dat"], magic : ["CHEMICAL molecule Data"]},
		fredFishProductInfo               : {name : "Fred Fish's Product-Info", magic : ["Fred Fish's Product-Info"]},
		gedcom                            : {name : "GEDCOM Genealogy Text", website : "http://fileformats.archiveteam.org/wiki/GEDCOM", ext : [".ged"], magic : ["GEDCOM genealogy text", "GEDCOM Family History", "GEDCOM genealogy, ASCII text", /^fmt\/851( |$)/]},
		gnuBisonGrammar                   : {name : "GNU Bison Grammar", ext : [".yy", ".y"], magic : ["GNU Bison grammar"], weakMagic : true},
		js                                : {name : "JavaScript", ext : [".js"], magic : ["JavaScript Source Code", "JavaScript source"], weakMagic : true},
		installProfessionalProject        : {name : "INSTALL Professional project", ext : [".dat"], magic : ["INSTALL Professional project"]},
		latexAUXFile                      : {name : "Latex Auxiliary File", ext : [".aux"], magic : ["LaTeX auxiliary file", "LaTeX table of contents"], weakMagic : true},
		lexDescriptionTextCSource         : {name : "lex description text C source", ext : [".l", ".y"], magic : ["lex description text C source, ASCII text"], weakMagic : true},
		lightWaveScene                    : {name : "LightWave Scene", website : "http://fileformats.archiveteam.org/wiki/LightWave_Scene", ext : [".lws", ".scn"], magic : ["LightWave 3D Scene"]},
		lingoScript                       : {name : "Lingo Script", filename : [/^lingoScript$/, /^lingoScript_\d+$/], magic : TEXT_MAGIC, weakMagic : true},
		lisp                              : {name : "Lisp/Scheme", website : "http://fileformats.archiveteam.org/wiki/LISP", ext : [".lsp"], magic : ["Lisp/Scheme program"]},
		m4                                : {name : "M4 Source File", website : "http://fileformats.archiveteam.org/wiki/M4", ext : [".m4"], magic : ["m4 preprocessor / macro source", "M4 macro processor script"], weakMagic : true},
		modulaDefinition                  : {name : "Modula Definition", ext : [".def"], magic : ["Modula Definitionsdatei"]},
		modulaImplementation              : {name : "Modula Implementation", ext : [".mod"], magic : ["Modula Implementierungsdatei"]},
		moduleDescriptionFile             : {name : "Module Description File", website : "http://fileformats.archiveteam.org/wiki/MDZ", ext : [".mdz"], magic : ["Open Cubic Player Module Information MDZ"]},
		neoBookDocument                   : {name : "NeoBook Document", ext : [".pub"], magic : ["NeoBook for DOS document"]},
		pas                               : {name : "Pascal/Delphi Source File", website : "http://fileformats.archiveteam.org/wiki/Pascal", ext : [".pas", ".tp5"], magic : [...TEXT_MAGIC, "Delphi Project source", "Pascal Programm", "Pascal Source Code 'DOS'", "Pascal source"], weakMagic : true},
		pemCertificate                    : {name : "PEM Certificate", ext : [".cer"], magic : ["PEM certificate", "Internet Security Certificate"]},
		perlPODDocument                   : {name : "Perl POD Document", ext : [".pm"], magic : ["Perl POD document"]},
		pgpPublicKey                      : {name : "PGP Public Key", website : "http://fileformats.archiveteam.org/wiki/PGP_public_key", ext : [".asc", ".aexpk", ".pgp", ".pub"], magic : ["PGP public key block", "PGP armored data, public key block"]},
		pgpMessage                        : {name : "PGP Message", website : "http://fileformats.archiveteam.org/wiki/PGP", magic : ["PGP signed message", "PGP clear text signed message", "PGP ASCII-Armor", "PGP message, ASCII text", "PGP Nachricht", /^PGP message$/, /^PGP armored data, (signed )?message/]},
		php                               : {name : "PHP Script", website : "http://fileformats.archiveteam.org/wiki/PHP", ext : [".php", ".phps"], magic : ["PHP source", "PHP script"], weakMagic : true},
		ppd                               : {name : "PostScript Printer Description", website : "http://fileformats.archiveteam.org/wiki/PostScript_Printer_Description", ext : [".ppd", ".pp"], magic : ["PPD file", "PostScript Printer Description"]},
		ps2MicroChannelAdapterDescription : {name : "PS/2 MicroChannel Adapter Description", ext : [".adf"], magic : ["PS/2 MicroChannel Adapter Description File"], weakMagic : true},
		reg                               : {name : "Windows Registry Data", website : "http://fileformats.archiveteam.org/wiki/Windows_Registry", ext : [".reg", ".dat"], magic : [/^Windows Registry (Data|text)/, "Windows Registry Datei", "MS Windows 95/98/ME registry file"]},
		rexx                              : {name : "OS/2 REXX Batch file", website : "https://www.tutorialspoint.com/rexx/index.htm", ext : [".rexx", ".rex"], magic : ["OS/2 REXX batch file", ...TEXT_MAGIC], weakMagic : true},
		scalaMultimediaScript             : {name : "Scala Multimedia Script", ext : [".script"], magic : ["Scala Multimedia Script (generic)"]},
		sgml                              : {name : "SGML Document", website : "http://fileformats.archiveteam.org/wiki/SGML", ext : [".sgml"], magic : ["exported SGML document", "HyperText Markup Language"], weakMagic : true},
		stormEdSettings                   : {name : "StormEd settings", ext : [".ed"], magic : ["StormEd settings"]},
		stormShellProjectMakefile         : {name : "Storm Shell project/makefile", ext : [".¶", ".image"], magic : ["Storm Shell project/makefile"]},
		traconSimulationData              : {name : "Tracon Simulation data", ext : [".dem", ".sim"], magic : ["Tracon Simulation data"]},
		vendinfo                          : {name : "VENDINFO", ext : [".diz"], filename : [/^vendinfo\.diz$/i], magic : ["VENDINFO information"]},
		videoFX2Effect                    : {name : "VideoFX2 Effect", ext : [".vfx"], magic : ["VideoFX2 Effect"]},
		videoFX2Script                    : {name : "VideoFX2 Script", ext : [".script"], magic : ["VideoFX2 Script"]},
		wavefrontMaterial                 : {name : "Wavefront Material", website : "http://fileformats.archiveteam.org/wiki/Wavefront_MTL", ext : [".mtl"], magic : ["Alias|Wavefront material", /^fmt\/1211( |$)/]},
		windowsAutorun                    : {name : "Windows Autorun File", website : "http://fileformats.archiveteam.org/wiki/INF_(Windows)", ext : [".nf"], filename : [/^autorun.inf$/i], magic : ["Microsoft Windows Autorun file", "AutoRun Info", "INF Datei [AutoRun]", /^fmt\/331( |$)/]},
		windowsSetupINFormation           : {name : "Windows Setup INFormation", website : "http://fileformats.archiveteam.org/wiki/INF_(Windows)", magic : ["Windows setup INFormation", "Windows driver setup Information", "INF Datei [Version]", /^x-fmt\/420( |$)/]},
		winJackForMSWin                   : {name : "WinJack for MS Win", ext : [".bj"], magic : ["WinJack for MS Win game variant (v1.x)"]}
	}
};
