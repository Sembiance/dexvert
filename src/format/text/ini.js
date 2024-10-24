import {Format} from "../../Format.js";

export class ini extends Format
{
	name           = "INI File";
	website        = "http://fileformats.archiveteam.org/wiki/INI";
	ext            = [".ini", ".inf", ".cfg", ".conf", ".nfo"];
	forbidExtMatch = [".cfg", ".conf", ".nfo"];
	magic          = [
		// general INI types
		"Generic INI configuration", "Windows desktop.ini", "INF Datei", "Windows Initialization settings",

		// specific INI Types: We keep these identified as 'ini' due to the untouch and 'metaProvider' check. I could in the future create a new format for each of these, but I'd have to include thoses checks below (maybe after I update formats.js to better handle this)
		"InstallShield Setup config", "Windows Dial-Up Networking configuration", "Microsoft Setup Toolkit for Windows files List", "LapLink 5 settings", "InstallShield Language Identifier", "TagInfo data", "TagInfo, ASCII text", "Delphi project Options",
		"BRIEF session info", "Windows Explorer Command Shell File", "Windows Explorer Shell Command File", "AOL Modem parameters", "McAfee VirusScan for Windows settings", "Microsoft C/C++ project Status info", "Blob Sculptor for Windows model", "TagInfo",
		"WinAmp/SHOUTcast PlayList", "Delphi Options File", "KDE/GNOME desktop entry", "WS_FTP configuration", "Iavadraw Wizard", "Wired For Sound configuration", "Karaoke track info", "Superbase printer driver", "KDE desktop entry", "UltraEdit Project",
		"CloneCD CDImage (description)", "MOdule (play)List", "Exchange Extended Configuration File - Office Add-in", "JBuilder Beans Descriptor", "Premiere Motion settings", "Microsoft ODBC Data Source", "Premiere project", "Bloodshed Dev-C++ project",
		"3ds UI colors", "NextSTART Theme", "The Chessmaster 4000 layout", "MS Flight Simulator aircraft configuration file", "Spring Engine unit Info", "Total Annihilation Main Unit Definition", "Winamp Signal Processing Studio DSP-Effect", "WinZip Job File",
		"SpyBot-Search-and-Destroy malware info", "ArcExplorer Project", "PaintTool SAI Tool parameters", "J.River Media Center plugin", "NetCaptor's CaptorGroup", "Delphi project Desktop", "Symantec Guard Header", "Turbo Fractal Generator settings",
		"DrumSynth Preset", "WinRIX configuration", "TsiLang translation data", "audio/x-scpls", "Entrust Entelligence Profile", "Inno Setup Script", "application/x-netshow-channel", "Windows CONTROL.INI", "CDROM Drive Analyzer configuration (v2.x)",
		"RivaTuner data base Build", "VIA setup configuration", "Soldat Bot Information", "blueMSX machine settings", "WinAPE configuration", "text/x-dbus-service", "Windows IOS.INI", "MPLAB IDE Project", "yum Repository configuration",
		"Windows system Initialization settings", "EightyOne snapshot", "Icon Theme index", "Cisco VPN Profile Configuration File", /^Avatar Studio (Deformations|data \(generic\)|SAP|Save|Animation|BRZ|Bank descriptor)/, "Room Arranger design",
		"AGS game configuration", "Picasa info (generic)", "Adblock Plus 2.0 rules file", "KLH10 RAW tape image directory", "Marble map description", "Advanced Renamer method", "D-Fend Reloaded Profile", "RawTherapee Postprocessing Profile",
		"Psycle display preset", "cdrtfe tools configuration", "SynWrite Output Preset", "Midnight Commander skin", "NPS Image Editor Palette", "Silverpoint Skin", "SlickRun MagicWord Pack", "Krita Color scheme", "Compaq Diagnostics",
		"Windows Media redirector / shortcut", /^Motocross Madness (model|Motions|Scene)/, /^CloneCD CD-image Description/, /^PLS playlist/, /^Windows [Cc]odepage translator/, /^InstallShield Project$/,
		/^fmt\/(1456|1614|1760)( |$)/
	];
	priority       = this.PRIORITY.LOWEST;
	untouched      = dexState => dexState.meta.valid && (dexState.meta.sectionNames || []).length>0;
	metaProvider   = ["text", "iniInfo"];
}
