"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu"),
	C = require("../C.js");

// All of the formats in this file are automatically 'unsupported' and are not processed, but can still be 'identified'
exports.formats =
{
	executable :
	{
		amigaExe     : {name : "AmigaOS Executable", magic : ["AmigaOS loadseg()ble executable/binary", "Amiga Hunk executable"]},
		atariCPX     : {name : "Atari Control Panel Extension Module", ext : [".cpx"], magic : ["Atari 68xxx CPX file", "Atari Control Panel applet"], weakMagic : true},
		atariSTExe   : {name : "Atari ST Executable", magic : ["Atari ST TOS executable", "Atari ST M68K contiguous executable", "Atari ST program/executable"]},
		com          : {name : "MS-DOS COM Executable", ext : [".com", ".c0m"], magic : ["DOS executable (COM", /^COM executable for (MS-)?DOS/, "16bit COM executable", "16bit DOS COM"]},
		elf          : {name : "ELF Executable", magic : ["ELF Executable and Linkable format", /^ELF \d\d-bit [LM]SB executable/, "Executable and Linkable Format"]},
		omagic       : {name : "Linux OMAGIC Executable", magic : ["Linux i/386 OMAGIC executable", "Linux/i386 impure executable (OMAGIC)"]},
		msDOSDriver  : {name : "MS-DOS Driver", ext : [".sys", ".drv"], magic : [/^DOS executable \(.+ device driver/], weakMagic : true},
		xex          : {name : "Atari Executable", ext : [".xex"], magic : ["Atari XE Executable"], weakMagic : true}
	},
	
	rom :
	{
		gameBoy : {name : "Game Boy ROM", ext : [".gb", ".gbc"], magic : ["GameBoy Color ROM File", "Game Boy ROM image"]}
	},

	other :
	{
		// Various unsupported file formats. Not very interesting formats.
		adobeTypeFontInfo            : {name : "Adobe Type Manager Font Information", ext : [".inf"], magic : ["Adobe Type Manager Font Information"]},
		ailMidiDriver                : {name : "Audio Interface Library 3 Music/MIDI driver", ext : [".mdi"], magic : ["Audio Interface Library 3 Music/MIDI driver"]},
		ailDigitalAudioDriver        : {name : "Audio Interface Library 3 Digital audio driver", ext : [".dig"], magic : ["Audio Interface Library 3 Digital audio driver"]},
		alchemyMindworksResource     : {name : "Alchemy Mindworks Resource", ext : [".res"], magic : ["Alchemy Mindworks Resource data"]},
		amigaActionReplay3           : {name : "Amiga Action Replay 3 Freeze File", magic : ["Amiga Action Reply 3 Freeze File"]},
		amigaBlkDev                  : {name : "Amiga ADF BlkDev File", ext : [".blkdev"], magic : [...C.TEXT_MAGIC, /^data$/], weakMagic : true},
		amigaBootCode                : {name : "Amiga ADF Bootcode", ext : [".bootcode"], magic : [...C.TEXT_MAGIC, /^data$/], weakMagic : true},
		amigaCLIMateDirIndex         : {name : "Amiga CLI-Mate Directory Index File", filename : [".fastdir"]},
		amigaLibrary                 : {name : "Amiga Hunk Library/Object", ext : [".lib", ".obj", ".o"], magic : ["AmigaOS object/library data", "Amiga Hunk library/object code"]},
		amigaSharedLibrary           : {name : "Amiga Shared Library", ext : [".lib"], magic : ["AmigaOS shared library"]},
		amigaXDFMeta                 : {name : "Amiga ADF XDF Meta", ext : [".xdfmeta"], magic : [...C.TEXT_MAGIC, /^data$/], weakMagic : true},
		amosAmalBank                 : {name : "Amos Amal Animation Bank", ext : [".abk"], magic : ["AMOS AMAL Bank"]},
		amosDatasBank                : {name : "AMOS Datas Bank", ext : [".abk"], magic : ["AMOS Data Bank", "AMOS Memory Bank, Data format"]},
		asciiFontMetrics             : {name : "ASCII Font Metrics", ext : [".afm"], magic : ["ASCII font metrics", "Outline Font Metric"]},
		atariGEMOBM                  : {name : "Atari GEM OBM File", ext : [".obm"], magic : ["Atari GEM OBM File"]},
		asymetrixToolbook            : {name : "Asymetrix ToolBook File", ext : [".tbk"], magic : ["Asymetrix ToolBook"]},
		borlandDelphiBuilderForm     : {name : "Borland Delphi - C++ Builder Form", ext : [".dfm"], magic : ["Borland Delphi - C++ Builder Form"]},
		borlandDelphiCompiledUnit    : {name : "Borland Delphi Compiled Unit", ext : [".dcu"], magic : ["Borland Delphi .DCU file"]},
		borlandDrive                 : {name : "Borland Graphics Interface Driver", ext : [".bgi"], magic : ["Borland Graphics Interface driver", "Borland device BGI Device Driver"]},
		borlandOverlay               : {name : "Borland Overlay", ext : [".ovr"], magic : ["Borland Overlay"]},
		borlandTurboCProject         : {name : "Borland Turbo C Project", ext : [".prj"], magic : ["Borland Turbo C Project"]},
		boyanActionModule            : {name : "BOYAN Action Model", ext : [".bam"], magic : ["BOYAN Action Module"]},
		chaosultdGEMParameters       : {name : "CHAOSultdGEM Parameters", ext : [".chs"], magic : ["CHAOSultdGEM parameters"]},
		chemViewAnimationData        : {name : "Chemview Animation Data", ext : [".d"], magic : ["CHEMVIEW animation Data"]},
		corncob3DData                : {name : "Corncob 3D Data File", ext : [".cct"], magic : ["Corncob 3D Theater-of-operation data"]},
		creativeSignalMicrocode      : {name : "Creative Signal Processor microcode", ext : [".csp"], magic : ["Creative Signal Processor microcode"]},
		cygnusEdDefaultSettings      : {name : "Cygnus Editor Default Settings", filename : ["ceddefaults"], magic : ["CygnusEd default settings"]},
		cygnusEdMacros               : {name : "Cygnus Editor Macros", filename : ["cedmacros"], magic : ["CygnusEd macros"]},
		dBaseIndex                   : {name : "dBase Index File", ext : [".ntx"]},
		emacsCompiledLisp            : {name : "Emacs Compiled Lisp", ext : [".elc"], magic : [/^Emacs .*byte-compiled Lisp data$/], notes : "Could decompile it with: https://github.com/rocky/elisp-decompile"},
		foxProMemo                   : {name : "FoxPro Memo File", ext : [".fpt"], magic : ["Microsoft FoxPro Memo", "FoxPro FPT", "Sybase iAnywhere memo files"]},
		fullTiltPinballData          : {name : "Full Tilt Pinball Data", ext : [".dat"], magic : ["Full Tilt! Pinball table data"]},
		gfaBasicWindows              : {name : "GFA-BASIC Windows", ext : [".gfw"], magic : ["GFA-BASIC Windows v3 tokenized source"]},
		iccColorProfile              : {name : "ICC Color Profile", ext : [".icc"], magic : ["ICC Color profile", /^color profile/]},
		iffDTYP                      : {name : "Amiga IFF DTYP", magic : ["Amiga IFF datatype info", "IFF data, DTYP datatype description"]},
		iffPrefs                     : {name : "Amiga Preferences", ext : [".prefs"], magic : ["Amiga Preferences", "IFF data, PREF preferences"]},
		iffSDBG					     : {name : "Amiga IFF Debug File", ext : [".debug"], magic : ["IFF SDBG file"]},
		installShieldScript          : {name : "InstallShield Script", ext : [".ins"], magic : ["InstallShield Script"]},
		installShieldUninstallScript : {name : "InstallShield Uninstall Script", ext : [".isu"], magic : ["InstallShield Uninstall Script"]},
		javaClass                    : {name : "Java Class File", ext : [".class"], magic : ["Java Compiled Object Code", "compiled Java class data", "Java bytecode"]},
		legendOfKyrandiaEMCFile		 : {name : "Legend of Kyrandia EMC File", ext : [".emc"], magic : ["Kyra Engine game data"]},
		lotus123FormattingData       : {name : "Lotus 1-2-3 Formatting Data", ext : [".fm3"], magic : ["Formatting Data for Lotus 1-2-3 worksheet"]},
		neoPaintPallette             : {name : "NeoPaint Palette", ext : [".pal"], magic : ["NeoPaint Palette"]},
		neoPaintPrinterDriver        : {name : "NeoPaint Printer Driver", ext : [".prd"], magic : ["NeoPaint Printer Driver"]},
		mdiffPatchFile               : {name : "MDIFF Patch File", ext : [".mdf"], magic : ["MDIFF patch"]},
		microLatheObject             : {name : "Micro Lathe Object", ext : [".lat"], magic : ["MicroLathe object"]},
		milesSoundSystemDriver       : {name : "Miles Sound System Driver", ext : [".adv"], magic : ["Miles Sound System real mode drivers"]},
		msvcRes                      : {name : "MSVC Resource File", ext : [".res"], magic : ["MSVC .res"]},
		netwareLoadableModule        : {name : "Netware Loadable Module", ext : [".nlm"], magic : [/^Net[Ww]are Loadable Module/]},
		netwareMessage               : {name : "Netware Message", ext : [".msg"], magic : ["NetWare Message"]},
		nortonChangeDirInfo          : {name : "Norton Change Directory Info", ext : [".ncd"], magic : ["Norton Change Directory info"]},
		noteWorthyCompsure           : {name : "NoteWorthy Composure", ext : [".nw"], magic : ["NoteWorthy song"]},
		objectVisionDatafile         : {name : "ObjectVision Datafile", ext : [".ovd"], magic : ["ObjectVision Datafile"]},
		olbLib                       : {name : "OLB Library", magic : ["OLB Library"]},
		pascalCompiledUnit           : {name : "Pascal Compiled Unit", ext : [".tpu", ".ppu"], magic : ["Borland Turbo Pascal compiled Unit", "FreePascal compiled Unit", "Pascal unit"]},
		polyfilmPrefs                : {name : "Polyfilm Preferences", ext : [".prf"], magic : ["Polyfilm Preferences"]},
		printerFontMetrics           : {name : "Printer Font Metrics", ext : [".pfm"], magic : ["Adobe Printer Font Metrics", "Printer Font Metrics"]},
		riffMSXF                     : {name : "RIFF MSFX File", ext : [".sfx"], magic : ["RIFF MSFX file"], notes : "Just contains meta info about a given soundeffect usually distributed alongside it as a .wav"},
		riffMxSt                     : {name : "RIFF MxSt File", ext : [".si"], magic : ["RIFF MxSt file"], notes : "References to other files, seems to be meta info only. Only info I could find, failed to process: https://github.com/dutchcoders/extract-riff"},
		riffSTYL                     : {name : "RIFF STYL File", ext : [".par"], magic : ["RIFF STYL file"], notes : "References a font for mac and windows and includes some text in a TEXT chunk"},
		rtPatchFile                  : {name : "RTPatch File", ext : [".rtp"], magic : ["RTPatch update/diff data"]},
		starTrekkerModuleInfo        : {name : "Startrekker Module Info", ext : [".nt"], magic : [/^Startrekker .*module info$/]},
		stormWizardResource          : {name : "StormWizard Resource", ext : [".wizard", ".wizard-all"], magic : ["IFF data, WZRD StormWIZARD resource", "StormWIZARD resource"]},
		turboBASICChainModule        : {name : "Turbo Basic Chain module", ext : [".tbc"], magic : ["Turbo Basic compiled Chain module"]},
		turboCContextFile            : {name : "Turbo C Context File", ext : [".dsk"], magic : ["Turbo C Context"]},
		turboPascalChainModule       : {name : "Turbo Pascal Chain module", ext : [".chn"], magic : ["Turbo Pascal 2.0 Chain module"]},
		turboPascalHelp              : {name : "Turbo Pascal Help", ext : [".hlp"], magic : ["Turbo Pascal Help"]},
		turboPascalOverlay           : {name : "Turbo Pascal Overlay", ext : [".ovr"], magic : ["Turbo Pascal Overlay"]},
		visualBasicExtension         : {name : "Visual Basic Extension", ext : [".vbx"], magic : ["Visual Basic eXtension/Custom Control"]},
		visualCLibrary               : {name : "Microsoft Visual C Library", ext : [".lib"], magic : ["Microsoft Visual C Library"]},
		windowsHelpFileContent       : {name : "Microsoft Windows Help File Content", ext : [".cnt"], magic : ["Help File Contents", "MS Windows help file Content"], notes : "Just a table of contents as to what's in the corresponding .hlp file. Not useful."},
		windowsHelpGIDIndex          : {name : "Windows Help Global Index Data", ext : [".gid"], magic : ["GID Help index", "MS Windows help Global Index"]},
		windowsProgramGroup          : {name : "Windows Program Group", ext : [".grp"], magic : ["Windows Program Manager Group", "Windows 3.x .GRP file"]},
		windowsProgramInfo           : {name : "Microsoft Windows Program Information File", ext : [".pif"], magic : ["Program Information File (Windows)", "Windows Program Information File"]},
		windowsShortcut              : {name : "Windows Shortcut", ext : [".lnk"], magic : ["Windows Shortcut", "MS Windows shortcut"]},
		wordPerfectKeyboardFile      : {name : "WordPerfect keyboard file", ext : [".wpk"], magic : ["WordPerfect keyboard file"]},
		wordPerfectMacro             : {name : "WordPerfect Macro File", ext : [".wpm"], magic : [/^WordPerfect [Mm]acro/]}
	}
};
