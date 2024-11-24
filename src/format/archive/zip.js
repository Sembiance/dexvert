import {Format} from "../../Format.js";
import {RUNTIME} from "../../Program.js";

export class zip extends Format
{
	name           = "PKZip Archive";
	website        = "http://fileformats.archiveteam.org/wiki/ZIP";
	ext            = [".zip", ".exe"];
	forbidExtMatch = [".exe"];
	magic          = [
		// general zip magic
		"ZIP compressed archive", "Zip data", "Zip archive", "ZIP Format", /ZIP self-extracting archive/, "Zip multi-volume archive data", "application/zip", /^Zip$/,
		"Self-extracting zip", "ZIP Archiv gefunden", "Archive: Zip", "Zip archive, with extra data prepended", "End of Zip archive", /^x-fmt\/263( |$)/,

		// app specific zip magic
		/^PKZIP (mini-)?self-extracting 16bit DOS executable$/, "Winzip Win32 self-extracting archive", "WinZip Self-Extractor", /^Quake 3 game data$/, "WinAmp 2.x Skin", "DivX Skin", "DesktopX Theme", "SPSS Extension", "Opera Widget", "FDI package",
		"Adventure Game Toolkit game package", "Installer: Alchemy Mindworks installer", "Installer: Wise Installer[ZIP]", "QWK offline mail packet (ZIP compressed)", "Q-emuLator Package", "Fritzing shareable project", "WinImage 32bit SFX disk image",
		"Universal Scene Description Zipped AR format (USDA)", "Konfabulator widget", "TorrentZip compressed archive", "Adobe Zipped Extension Package", "Java Web Archive", "Arkos Tracker Song (zipped)", "Installer: Acronis installer[ZIP]",
		"Speckie Dictionary Installation", "Apache OpenOffice AutoText configuration", "OpenDocument Database", "OpenOffice.org 1.x Database file", "Adobe Integrated Runtime", "TeamSpeak 3 Soundpack", "BSplayer Skin", "WinAmp 3.x / modern skin",
		"HoN Modification Manager package", /^Quintessential Player (Family|Kid) Skin/, "CursorXP theme", "BootSkin theme", "LogonStudio theme", "IconPackager theme", "JetFighter 2015 savegame", "iOS Application", "Flash Component distribution archive",
		"WinImage compressed disk image", "macOS application in a Zip container", "NuGet Package", "Microsoft Silverlight Application", "Silverlight Application Package", "Mozilla archive omni.ja", "Excel Macro-enabled Open XML add-in", "SvarDOS Package",
		"AutoCAD Custom User Interface", "Archive: CRX", /^Google Chrome [Ee]xtension/, "Movavi Video Editor Plus Project", "Titanium Backup Easy Backup saved data", "Compressed Google KML Document", "Mellel document", "Apple Mac OS X Dashboard Widget",
		"DashXL Dashboard", "Zip document container (generic)", "Fade In document", /^Python Egg$/, "MakerBot Thing", "Autodesk material Library", "Python Wheel package", "OpenOffice Extension (Dictionary)", "Microsoft Vista Sidebar Gadget (Zip)",
		"Balabolka Text document (compressed)", "Eclipse Project settings", "KMPlayer Skin File", "Nokia S60 Web Runtime Widget Package", "PotPlayer Skin", "Messenger Plus! Skin Pack", "MuseScore compressed music score", "Wise Care 365 Skin",
		"application/x-zip-compressed-fb2", "FreeCAD Standard document", "NumPy compressed data archive format", "Mozilla Firebird theme", /^Krita [Dd]ocument/, "application/x-krita", "osu! compressed beatmap data", "Wrapster archive (v1.0)",
		"LEGO Exchange Format - Digital Designer", "Minecraft LiteLoader Mod", "application/vnd.sun.xml.draw", "Samurize package", "OpenIV mod package", "Power BI report", "Sublime Text Package (generic)", "Maxthon skin (MX1)", "Pencil template",
		"Zoner Draw (container with preview)", "MediaForge Runtime Player Distribution Project", "Desktop Sidebar Panel", "Compressed Disk Image (password protected)", "DesktopX Object Package", "ComicRack plugin", "U3 application Package",
		/^fmt\/(424|524|595|627|628|937|943|999)( |$)/
	];
	weakMagic      = ["Zip archive, with extra data prepended"];
	idMeta         = ({macFileType, macFileCreator}) => ["pZIP", "ZIP "].includes(macFileType) || (macFileType==="xpi " && ["MzIn", "NSIn"].includes(macFileCreator));
	forbiddenMagic = ["SVArTracker module"];	// often mis-identified as a passworded zip file
	converters     = () =>
	{
		const r = ["sevenZip", "unzip", "deark[module:zip]", "deark[module:pklite]", "deark[module:zip][opt:zip:scanmode][strongMatch]", "unar", "sqc", "izArc[strongMatch][matchType:magic]"];
		
		// If we are macintoshjp, unar works best
		if(RUNTIME.globalFlags?.osHint?.macintoshjp)
		{
			r.removeOnce("unar");
			r.unshift("unar");
		}

		return r;
	};

	metaProvider   = ["zipInfo"];
	untouched      = dexState => dexState.hasMagics("Zip archive data (empty)");
	processed      = dexState =>
	{
		// reverse priority order
		for(const k of ["sevenZip", "unzip"])
			Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid===k)?.meta || {});
		
		if(dexState.meta.passwordProtected)
		{
			// can't do this in a 'untouched' callback because this meta data isn't available until after unzip converter has ran and the untouched method is called before converters
			dexState.untouched = true;
			return true;
		}

		return false;
	};
}
