"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu");

// All of the formats in this file are automatically 'unsupported' and are not processed, but can still be 'identified'
exports.formats =
{
	executable :
	{
		amigaExe : {name : "AmigaOS Executable", magic : ["AmigaOS loadseg()ble executable/binary", "Amiga Hunk executable"]},
		com      : {name : "MS-DOS COM Executable", ext : [".com", ".c0m"], magic : ["DOS executable (COM", /^COM executable for (MS-)?DOS/, "16bit COM executable", "16bit DOS COM"]},
		dll      : {name : "Microsoft Windows Dynmic Link Library", ext : [".dll"], magic : ["Win32 Dynamic Link Library"]},
		elf      : {name : "ELF Executable", magic : ["ELF Executable and Linkable format", /^ELF \d\d-bit [LM]SB executable/, "Executable and Linkable Format"]},
		exe      : {name : "MS-DOS/Windows Executable", ext : [".exe", ".scr"], magic : ["Generic Win/DOS Executable", "DOS Executable Generic", /MS-DOS [Ee]xecutable/, /^Win\d\d Executable/]},
		sys      : {name : "MS-DOS Driver", ext : [".sys", ".drv"], magic : [/^DOS executable \(.+ device driver/]},
		macExe   : {name : "MacOS Executable", magic : ["Macintosh Application (MacBinary)", "Preferred Executable Format"]},
		omagic   : {name : "Linux OMAGIC Executable", magic : ["Linux i/386 OMAGIC executable", "Linux/i386 impure executable (OMAGIC)"]}
	},

	rom :
	{
		gameBoy : {name : "Game Boy ROM", ext : [".gb", ".gbc"], magic : ["GameBoy Color ROM File", "Game Boy ROM image"]}
	},

	other :
	{
		// Various unsupported file formats. Not very interesting formats.
		adobeTypeFontInfo        : {name : "Adobe Type Manager Font Information", ext : [".inf"], magic : ["Adobe Type Manager Font Information"]},
		ailMidiDriver            : {name : "Audio Interface Library 3 Music/MIDI driver", ext : [".mdi"], magic : ["Audio Interface Library 3 Music/MIDI driver"]},
		ailDigitalAudioDriver    : {name : "Audio Interface Library 3 Digital audio driver", ext : [".dig"], magic : ["Audio Interface Library 3 Digital audio driver"]},
		alchemyMindworksResource : {name : "Alchemy Mindworks Resource", ext : [".res"], magic : ["Alchemy Mindworks Resource data"]},
		amigaActionReplay3       : {name : "Amiga Action Replay 3 Freeze File", magic : ["Amiga Action Reply 3 Freeze File"]},
		amigaCLIMateDirIndex     : {name : "Amiga CLI-Mate Directory Index File", filename : [".fastdir"]},
		amosAmalBank             : {name : "Amos Amal Animation Bank", ext : [".abk"], magic : ["AMOS AMAL Bank"]},
		amosDatasBank            : {name : "AMOS Datas Bank", ext : [".abk"], magic : ["AMOS Data Bank", "AMOS Memory Bank, Data format"]},
		asciiFontMetrics         : {name : "ASCII Font Metrics", ext : [".afm"], magic : ["ASCII font metrics", "Outline Font Metric"]},
		asymetrixToolbook        : {name : "Asymetrix ToolBook File", ext : [".tbk"], magic : ["Asymetrix ToolBook"]},
		borlandDrive             : {name : "Borland Graphics Interface Driver", ext : [".bgi"], magic : ["Borland Graphics Interface driver", "Borland device BGI Device Driver"]},
		borlandTurboCProject     : {name : "Borland Turbo C Project", ext : [".prj"], magic : ["Borland Turbo C Project"]},
		chemViewAnimationData    : {name : "Chemview Animation Data", ext : [".d"], magic : ["CHEMVIEW animation Data"]},
		corncob3DData            : {name : "Corncob 3D Data File", ext : [".cct"], magic : ["Corncob 3D Theater-of-operation data"]},
		creativeSignalMicrocode  : {name : "Creative Signal Processor microcode", ext : [".csp"], magic : ["Creative Signal Processor microcode"]},
		cygnusEdDefaultSettings  : {name : "Cygnus Editor Default Settings", filename : ["ceddefaults"], magic : ["CygnusEd default settings"]},
		cygnusEdMacros           : {name : "Cygnus Editor Macros", filename : ["cedmacros"], magic : ["CygnusEd macros"]},
		dBaseIndex               : {name : "dBase Index File", ext : [".ntx"]},
		foxProMemo               : {name : "FoxPro Memo File", ext : [".fpt"], magic : ["Microsoft FoxPro Memo", "FoxPro FPT", "Sybase iAnywhere memo files"]},
		fullTiltPinballData      : {name : "Full Tilt Pinball Data", ext : [".dat"], magic : ["Full Tilt! Pinball table data"]},
		iffCTLG                  : {name : "Amiga IFF Catalog", ext : [".catalog"], magic : ["IFF data, CTLG message catalog", "Amiga Catalog translation format"]}, // Just has app strings, see my ctlg2json app
		iffDTYP                  : {name : "Amiga IFF DTYP", magic : ["Amiga IFF datatype info", "IFF data, DTYP datatype description"]},
		iffPrefs                 : {name : "Amiga Preferences", ext : [".prefs"], magic : ["Amiga Preferences", "IFF data, PREF preferences"]},
		neoPaintPallette         : {name : "NeoPaint Palette", ext : [".pal"], magic : ["NeoPaint Palette"]},
		neoPaintPrinterDriver    : {name : "NeoPaint Printer Driver", ext : [".prd"], magic : ["NeoPaint Printer Driver"]},
		milesSoundSystemDriver   : {name : "Miles Sound System Driver", ext : [".adv"], magic : ["Miles Sound System real mode drivers"]},
		nortonChangeDirInfo      : {name : "Norton Change Directory Info", ext : [".ncd"], magic : ["Norton Change Directory info"]},
		printerFontMetrics       : {name : "Printer Font Metrics", ext : [".pfm"], magic : ["Adobe Printer Font Metrics", "Printer Font Metrics"]},
		riffMSXF                 : {name : "RIFF MSFX File", ext : [".sfx"], magic : ["RIFF MSFX file"]}, // Just contains meta info about a given soundeffect usually distributed alongside it as a .wav
		riffMxSt                 : {name : "RIFF MxSt File", ext : [".si"], magic : ["RIFF MxSt file"]}, // References to other files, seems to be meta info only. Only info I could find, failed to process: https://github.com/dutchcoders/extract-riff
		riffSTYL                 : {name : "RIFF STYL File", ext : [".par"], magic : ["RIFF STYL file"]}, // References a font for mac and windows and includes some text in a TEXT chunk
		starTrekkerModuleInfo    : {name : "Startrekker Module Info", ext : [".nt"], magic : [/^Startrekker .*module info$/]},
		turboBASICChainModule    : {name : "Turbo Basic Chain module", ext : [".tbc"], magic : ["Turbo Basic compiled Chain module"]},
		turboCContextFile        : {name : "Turbo C Context File", ext : [".dsk"], magic : ["Turbo C Context"]},
		turboPascalCompiledUnit  : {name : "Turbo Pascal Compiled Unit", ext : [".tpu"], magic : ["Borland Turbo Pascal compiled Unit"]},
		turboPascalOverlay		 : {name : "Turbo Pascal Overlay", ext : [".ovr"], magic : ["Turbo Pascal Overlay"]},
		visualBasicExtension     : {name : "Visual Basic Extension", ext : [".vbx"], magic : ["Visual Basic eXtension/Custom Control"]},
		visualCLibrary           : {name : "Microsoft Visual C Library", ext : [".lib"], magic : ["Microsoft Visual C Library"]},
		windowsHelpFileContent   : {name : "Microsoft Windows Help File Content", ext : [".cnt"], magic : ["Help File Contents", "MS Windows help file Content"]}, // Just a table of contents as to what's in the corresponding .hlp file. Not useful.
		windowsProgramInfo       : {name : "Microsoft Windows Program Information File", ext : [".pif"], magic : ["Program Information File (Windows)", "Windows Program Information File"]},
		wordPerfectKeyboardFile  : {name : "WordPerfect keyboard file", ext : [".wpk"], magic : ["WordPerfect keyboard file"]},
		wordPerfectMacro         : {name : "WordPerfect Macro File", ext : [".wpm"], magic : [/^WordPerfect [Mm]acro/]}
	}
};
