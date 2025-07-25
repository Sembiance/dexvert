import {Format} from "../../Format.js";

const _INSTALLER_MAGICS = [
	// installers: These actually do convert ok already with things like cmdTotal or other programs below
	"Installer: Vise", "16bit DOS EXE SEZ sfx Zoo archive",

	// installers - NOTE: It would be nice to find a way to 'properly' extract the contents of all these installers (note: some of these may already be handled correctly with cmdTotal extensions)
	"InstallShield setup", "Wise Installer executable",

	"Win16 EDI Install Pro executable", "Win16 InstallShield Self-Extracting Executable", "Easy SFX Installer 16-bit DOS executable", "JRchive self-extracting 16bit DOS executable", "aPackage sfx archiver Win32 executable",

	"Installer: Gentee Installer", "Installer: Eschalon Installer", "Installer: AOLSetup", "Installer: Pantaray QSetup", "Installer: STATICSUP", "Installer: O'Setup95", "Installer: Setup Factory", "Installer: Tarma Installer", "Installer: InstallUs",
	"Installer: LucasArts Update Installer", "Installer: CreateInstall", "Installer: PCInstall", "Installer: Setup-Specialist", "Installer: GPInstall", "Installer: Silver Creek Entertainment[zlib]", "Installer: CSDD's installer", "Installer: RNsetup",
	"Installer: InstallAnywhere", "Installer: ClickTeam", "Installer: Aeco Systems installer", "Installer: Winamp Installer", "Installer: PIMP Installer", "Installer: Spoon Installer", "Installer: Ghost Installer", "Installer: Squirrel Installer",
	"Installer: Multimedia Fusion Installer", "Installer: Multimedia Fusion Installer", "Installer: Blizzard PrePatch(2.xx)", "Installer: Box Stub", "Installer: WiX Toolset installer", "Installer: BitRock Installer", "Installer: Tarma InstallMate",
	"Installer: Mioplanet installer", "Installer: Install4j Installer", "Installer: QT installer", "Installer: Bytessence Install Maker", "Installer: TrueCrypt-VeraCrypt installer", "Installer: distutils installer", "Installer: Actual Installer",
	"Installer: VMWare Software Installer", "Installer: Excelsior Installer", "Installer: Smart Install Maker", "Installer: Sony Windows Installer", "Installer: Autorun Pro Enterprise II", "Installer: Adobe SVG Installer", "Installer: NOS Installer",
	"Installer: BulletProofSoft installer", "Installer: DeployMaster", "Installer: distutils", "Installer: INTENIUM install system", "Installer: CrypKey", "Installer: CSDD's", "Installer: I-D Media installer", "Installer: ACCAStore",
	"Installer: SwiftView Inc. installer",
	
	/^Installer: Wise Installer$/, /^NSIS$/
];

export class exe extends Format
{
	name    = "MS-DOS/Windows or OS/2 Executable";
	website = "http://fileformats.archiveteam.org/wiki/EXE";
	ext     = [".exe"];
	magic   = [
		// general exe type
		"Generic Win/DOS Executable", /MS-DOS [Ee]xecutable/, /^Win\d\d Executable/, /(compressed|compiled) DOS [Ee]xecutable$/, /^Microsoft .*DOS Executable/, "DOS Executable", "OS/2 Executable", "32bit DOS Executable", "deark: exe ",
		"Microsoft executable", /^PE32\+? executable/, /^Win\d\d Executable/, "Win16 NE executable", /^Ist eine ausf.hrbare (OS\/2|Win 3\.x|DOS|Win32)/, /^fmt\/(899|900)( |$)/, /^x-fmt\/(409|410|411)( |$)/,

		// specific exe types
		"JEMM memory manager", "Microsoft BASIC Compiler runtime", "DeskPic Screen Saver Module", "MS-DOS DJGPP go32 DOS extender executable", "OS/2 Presentation Manager Executable", "DOS/4G DOS Extender Executable", "MOZART tune",
		"Graphic Workshop self-displaying picture executable", "PE Unknown PE signature 0 (Control Panel Item)", "GIMP Plugin (Win)", "Total Commander Packer extension (plugin)", "WIFE Font Driver", "PhotoFilter plugin", "Win32 EXE RosAsm",
		"Total Commander Content plugin", "Total Commander File system extension (plugin)", "Lavasoft Ad-aware 6 plugin", "Find and Run Robot (FARR) plugin", "Microsoft Basic Quick library", "Flow Charting 3 Printer Definition", "Javelin Driver",
		"Win16 Klik'n'Play Executable (generic)", "16bit EXE DOS SCRNCH Executable",
		
		// icon libraries (these are EXEs basically with icons in them, the current tools below do a fine job at extracting the icons so no need to make a separate format for them)
		"Icon library (Impact Software)", "Icon library (Norton Icon Editor)", "Icon library (Easy Icons v3.x)", "Icon library (hDC Icon Designer)",

		// created by
		"Format: AutoIt(3.XX)", "DOS Turbo Basic executable", "REALbasic Win32 Executable", "GFA BASIC Win 3.x compiled Executable", "DOS Borland compiled Executable (generic)", /^(16-bit )?Microsoft (C|Visual C\+\+) compiled executable/,
		/^Microsoft Pascal (v[\d.]+ )?16-bit executable/, "16bit DOS EXE ApBasic", "MicroFocus COBOL DOS Executable", "16bit DOS EXE BasicBasic", "Turbo Pascal for Windows 1.0 executable", "MinGW32 C/C++ Executable", "Generic CIL Executable",
		"DOS Metaware Professional Pascal Executable", "Win32 Cygwin executable", "WIN32 Executable PowerBASIC", "DOS Pacific C Compiler executable", "Win32 EXE TMT Pascal (generic)", "Format: AutoIt", "Format: Compiled AutoHotKey",
		"AutoIt3 compiled script executable", "TCC Win32 executable", "Win32 EXE Euphoria (Watcom compiled)", "Win32 IBasic executable", "DIZ2EXE Win32 executable", "16bit COM 22NICE loader", "FreeBASIC Win32 executable (generic)",
		"TMT Pascal Compiler 3.90 DOS executable", "16bit DOS Central Point Anti-Virus immunized Executable", "16bit DOS EXE EPW password protected",

		..._INSTALLER_MAGICS
	];
	priority     = this.PRIORITY.LOW;
	metaProvider = ["winedump"];

	pre = dexState =>
	{
		// If we have meta from winedump and it's a DLL file, then delete the meta which will cause no converters to run
		if((dexState.meta?.fileheader?.characteristics || []).includes("DLL"))
			Object.clear(dexState.meta);
	};

	// We throw MSDOS/Win EXESs at various programs to try and get something useful out of them like embedded director files, cursors, icons, images, etc
	converters = dexState =>
	{
		if(!Object.keys(dexState.meta).length)
			return [];
		
		const r= [
			// Is it just a ZIP file of some sort?
			"sevenZip[type:zip]",
			
			// What about an NSIS installer?
			"sevenZip[type:nsis]",
			"unar[type:nsis]",

			// Is it a Projector executable hiding a director file?
			"director_files_extract"
		];

		// generic installer extractor
		r.push("cmdTotal[wcx:InstExpl.wcx]");

		// Try some general EXE extractors
		r.push("sevenZip[type:PE][rsrcOnly]", "deark[module:exe]");

		return r;
	};

	post = dexState =>
	{
		if(Object.keys(dexState.meta).length>0)
			dexState.processed = true;
	};
}

// Borland Delphi EXE/DLL extractor in sandbox/app/IDR/
// It's not really needed though, as the delphi forms are usually Resources that get extracted by sevenZip and then handled by my borlandDelphiForm program
