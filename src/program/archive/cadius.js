import {xu} from "xu";
import {Program} from "../../Program.js";
import {runUtil, fileUtil} from "xutil";
import {dateParse, path} from "std";

// FROM: https://www.kreativekorp.com/miscpages/a2info/filetypes.shtml
export const _PRO_DOS_TYPE_CODE = {"00" : "UNK", "01" : "BAD", "02" : "PCD", "03" : "PTX", "04" : "TXT", "05" : "PDA", "06" : "BIN", "07" : "FNT", "08" : "FOT", "09" : "BA3", "0A" : "DA3", "0B" : "WPF", "0C" : "SOS", "0F" : "DIR", "10" : "RPD", "11" : "RPI", "12" : "AFD", "13" : "AFM", "14" : "AFR", "15" : "SCL", "16" : "PFS", "19" : "ADB", "1A" : "AWP", "1B" : "ASP", "20" : "TDM", "21" : "IPS", "22" : "UPV", "29" : "3SD", "2A" : "8SC", "2B" : "8OB", "2C" : "8IC", "2D" : "8LD", "2E" : "P8C", "41" : "OCR", "42" : "FTD", "50" : "GWP", "51" : "GSS", "52" : "GDB", "53" : "DRW", "54" : "GDP", "55" : "HMD", "56" : "EDU", "57" : "STN", "58" : "HLP", "59" : "COM", "5A" : "CFG", "5B" : "ANM", "5C" : "MUM", "5D" : "ENT", "5E" : "DVU", "60" : "PRE", "6B" : "BIO", "66" : "NCF", "6D" : "DVR", "6E" : "PRE", "6F" : "HDV", "80" : "GES", "81" : "GEA", "82" : "GEO", "83" : "GED", "84" : "GEF", "85" : "GEP", "86" : "GEI", "87" : "GEX", "89" : "GEV", "8B" : "GEC", "8C" : "GEK", "8D" : "GEW", "A0" : "WP ", "AB" : "GSB", "AC" : "TDF", "AD" : "BDF", "B0" : "SRC", "B1" : "OBJ", "B2" : "LIB", "B3" : "S16", "B4" : "RTL", "B5" : "EXE", "B6" : "PIF", "B7" : "TIF", "B8" : "NDA", "B9" : "CDA", "BA" : "TOL", "BB" : "DRV", "BC" : "LDF", "BD" : "FST", "BF" : "DOC", "C0" : "PNT", "C1" : "PIC", "C2" : "ANI", "C3" : "PAL", "C5" : "OOG", "C6" : "SCR", "C7" : "CDV", "C8" : "FON", "C9" : "FND", "CA" : "ICN", "D5" : "MUS", "D6" : "INS", "D7" : "MDI", "D8" : "SND", "DB" : "DBM", "E0" : "LBR", "E2" : "ATK", "EE" : "R16", "EF" : "PAR", "F0" : "CMD", "F1" : "OVL", "F2" : "UD2", "F3" : "UD3", "F4" : "UD4", "F5" : "BAT", "F6" : "UD6", "F7" : "UD7", "F8" : "PRG", "F9" : "P16", "FA" : "INT", "FB" : "IVR", "FC" : "BAS", "FD" : "VAR", "FE" : "REL", "FF" : "SYS"};
export const _PRO_DOS_TYPE_PRETTY = {"00" : "Unknown", "01" : "Bad Block", "02" : "Pascal Code", "03" : "Pascal Text", "04" : "ASCII Text", "05" : "Pascal Data", "06" : "Binary File", "07" : "Apple III Font", "08" : "HiRes/Double HiRes Graphics", "09" : "Apple III BASIC Program", "0A" : "Apple III BASIC Data", "0B" : "Generic Word Processing", "0C" : "SOS System File", "0F" : "ProDOS Directory", "10" : "RPS Data", "11" : "RPS Index", "12" : "AppleFile Discard", "13" : "AppleFile Model", "14" : "AppleFile Report", "15" : "Screen Library", "16" : "PFS Document", "19" : "AppleWorks Database", "1A" : "AppleWorks Word Processing", "1B" : "AppleWorks Spreadsheet", "20" : "Desktop Manager File", "21" : "Instant Pascal Source", "22" : "UCSD Pascal Volume", "29" : "SOS Directory", "2A" : "Source Code", "2B" : "Object Code", "2C" : "Interpreted Code", "2D" : "Language Data", "2E" : "ProDOS 8 Code Module", "41" : "Optical Character Recognition", "42" : "File Type Definitions", "50" : "Apple IIgs Word Processing", "51" : "Apple IIgs Spreadsheet", "52" : "Apple IIgs Database", "53" : "Object Oriented Graphics", "54" : "Apple IIgs Desktop Publishing", "55" : "HyperMedia", "56" : "Educational Program Data", "57" : "Stationery", "58" : "Help File", "59" : "Communications", "5A" : "Configuration", "5B" : "Animation", "5C" : "Multimedia", "5D" : "Entertainment", "5E" : "Development Utility", "60" : "PC Pre-Boot", "6B" : "PC BIOS", "66" : "ProDOS File Navigator Command File", "6D" : "PC Driver", "6E" : "PC Pre-Boot", "6F" : "PC Hard Disk Image", "80" : "System File", "81" : "Desk Accessory", "82" : "Application", "83" : "Document", "84" : "Font", "85" : "Printer Driver", "86" : "Input Driver", "87" : "Auxiliary Driver", "89" : "Swap File", "8B" : "Clock Driver", "8C" : "Interface Card Driver", "8D" : "Formatting Data", "A0" : "WordPerfect", "AB" : "Apple IIgs BASIC Program", "AC" : "Apple IIgs BASIC TDF", "AD" : "Apple IIgs BASIC Data", "B0" : "Apple IIgs Source Code", "B1" : "Apple IIgs Object Code", "B2" : "Apple IIgs Library", "B3" : "Apple IIgs Application Program", "B4" : "Apple IIgs Runtime Library", "B5" : "Apple IIgs Shell Script", "B6" : "Apple IIgs Permanent INIT", "B7" : "Apple IIgs Temporary INIT", "B8" : "Apple IIgs New Desk Accessory", "B9" : "Apple IIgs Classic Desk Accessory", "BA" : "Apple IIgs Tool", "BB" : "Apple IIgs Device Driver", "BC" : "Apple IIgs Generic Load File", "BD" : "Apple IIgs File System Translator", "BF" : "Apple IIgs Document", "C0" : "Apple IIgs Packed Super HiRes", "C1" : "Apple IIgs Super HiRes", "C2" : "PaintWorks Animation", "C3" : "PaintWorks Palette", "C5" : "Object-Oriented Graphics", "C6" : "Script", "C7" : "Apple IIgs Control Panel", "C8" : "Apple IIgs Font", "C9" : "Apple IIgs Finder Data", "CA" : "Apple IIgs Icon File", "D5" : "Music", "D6" : "Instrument", "D7" : "MIDI", "D8" : "Apple IIgs Audio", "DB" : "DB Master Document", "E0" : "Archive", "E2" : "AppleTalk Data", "EE" : "EDASM 816 Relocatable Code", "EF" : "Pascal Area", "F0" : "ProDOS Command File", "F1" : "User Defined 1", "F2" : "User Defined 2", "F3" : "User Defined 3", "F4" : "User Defined 4", "F5" : "User Defined 5", "F6" : "User Defined 6", "F7" : "User Defined 7", "F8" : "User Defined 8", "F9" : "ProDOS-16 System File", "FA" : "Integer BASIC Program", "FB" : "Integer BASIC Variables", "FC" : "Applesoft BASIC Program", "FD" : "Applesoft BASIC Variables", "FE" : "EDASM Relocatable Code", "FF" : "ProDOS-8 System File"};
export const _PRO_DOS_TYPE_PRETTY_SUB =
{
	"2C" : {"8003" : "Apex Program File"},
	"50" : {"5445" : "Teach", "8001" : "DeluxeWrite", "8010" : "AppleWorks GS"},
	"51" : {"8010" : "AppleWorks GS"},
	"52" : {"8010" : "AppleWorks GS", "8011" : "AppleWorks GS Template", "8013" : "GSAS"},
	"53" : {"8010" : "AppleWorks GS"},
	"54" : {"8002" : "GraphicWriter", "8010" : "AppleWorks GS"},
	"55" : {"0001" : "HyperCard GS", "8001" : "Tutor-Tech", "8002" : "HyperStudio", "8003" : "Nexus"},
	"59" : {"8010" : "AppleWorks GS"},
	"BC" : {"4001" : "Nifty List Module", "4002" : "Super Info Module", "4004" : "Twilight Module", "4083" : "Marinetti Link Layer Module"},
	"C0" : {"0001" : "Packed Super HiRes", "0002" : "Apple Preferred Format", "0003" : "Packed QuickDraw II PICT"},
	"C1" : {"0001" : "QuickDraw PICT", "0002" : "Super HiRes 3200"},
	"C8" : {"0000" : "QuickDraw Bitmap Font", "0001" : "Pointless TrueType Font"},
	"D8" : {"0000" : "AIFF", "0001" : "AIFF-C", "0002" : "ASIF Instrument", "0003" : "Sound Resource", "0004" : "MIDI Synth Wave", "8001" : "HyperStudio Sound"},
	"E0" : {"0000" : "ALU", "0001" : "AppleSingle", "0002" : "AppleDouble Header", "0003" : "AppleDouble Data", "8000" : "Binary II", "8001" : "AppleLink ACU", "8002" : "ShrinkIt"},
	"E2" : {"FFFF" : "EasyMount Alias"}
};
export const _proDOSTypeCodeToPretty = typeCode => _PRO_DOS_TYPE_PRETTY[Object.map(_PRO_DOS_TYPE_CODE, (k, v) => ([v, k]))[typeCode]];

export class cadius extends Program
{
	website   = "https://github.com/mach-kernel/cadius";
	package   = "app-arch/cadius";
	bin       = "cadius";
	args      = r => ["EXTRACTVOLUME", r.inFile(), r.outDir()];

	// Cadius sticks the file type and aux code to the end of each file, get rid of it
	postExec = async r => await ((await fileUtil.tree(r.outDir({absolute : true}), {nodir : true})) || []).parallelMap(async fileOutputPath => await Deno.rename(fileOutputPath, fileOutputPath.replace(/#[\dA-F]{6}$/, "")));

	// cadius doesn't set dates, but knows about them if I do a CATALOG listing, so this function will do a listing and set proper dates
	post = async r =>
	{
		//const currentYear = new Date().getFullYear();
		const {stdout} = await runUtil.run("cadius", ["CATALOG", r.inFile(), "-V"], {cwd : r.cwd});
		r.meta.fileMeta = {};

		let currentFilePath = null;
		for(const line of stdout.split("\n"))
		{
			const {filePath} = line.match(/^\s*File Path\s+:\s*\/(?<filePath>.+)\s*$/)?.groups || {};
			if(filePath)
			{
				r.meta.fileMeta[filePath] = {};
				currentFilePath = filePath;
				continue;
			}

			const {day, month, year} = line.match(/^\s*File Modification Date\s+:\s*(?<day>\d{2})-(?<month>\w{3})-(?<year>\d{4})\s*$/)?.groups || {};
			if(day && month && year)
			{
				r.meta.fileMeta[currentFilePath].when = dateParse(`${day}-${["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].indexOf(month).toString().padStart(2, "0")}-${year} 12:12:12`, "dd-MM-yyyy HH:mm:ss");
				continue;
			}

			for(const [key, match] of [["proDOSType", "File Type"], ["proDOSTypeAux", "File Aux Type"]])
			{
				const {value} = line.match(new RegExp(`^\\s*${match}\\s+:\\s*(?<value>.+)\\s*$`))?.groups || {};
				if(value)
				{
					r.meta.fileMeta[currentFilePath][key] = value;
					if(key==="proDOSType")
					{
						if(_PRO_DOS_TYPE_CODE[value])
							r.meta.fileMeta[currentFilePath].proDOSTypeCode = _PRO_DOS_TYPE_CODE[value];
						
						if(_PRO_DOS_TYPE_PRETTY[value])
							r.meta.fileMeta[currentFilePath].proDOSTypePretty = _PRO_DOS_TYPE_PRETTY[value];
					}
				}
			}
		}

		if(Object.keys(_PRO_DOS_TYPE_PRETTY_SUB).includes(r.meta.fileMeta[currentFilePath]?.proDOSType) && Object.keys(_PRO_DOS_TYPE_PRETTY_SUB[r.meta.fileMeta[currentFilePath].proDOSType]).includes(r.meta.fileMeta[currentFilePath].proDOSTypeAux))
			r.meta.fileMeta[currentFilePath].proDOSTypePretty += ` (${_PRO_DOS_TYPE_PRETTY_SUB[r.meta.fileMeta[currentFilePath].proDOSType][r.meta.fileMeta[currentFilePath].proDOSTypeAux]})`;

		if(["06", "FC"].includes(r.meta.fileMeta[currentFilePath]?.proDOSType))
			r.meta.fileMeta[currentFilePath].proDOSLoadingAddress = r.meta.fileMeta[currentFilePath].proDOSTypeAux;
		
		if(r.meta.fileMeta[currentFilePath]?.proDOSType==="04")
		{
			if(r.meta.fileMeta[currentFilePath]?.proDOSTypeAux==="0000")
				r.meta.fileMeta[currentFilePath].proDOSSequential = true;
			else
				r.meta.fileMeta[currentFilePath].prodDOSRecordLength = r.meta.fileMeta[currentFilePath].proDOSTypeAux;
		}

		for(const outputFile of r.f.files.new || [])
		{
			const relPath = path.relative(r.outDir(), outputFile.rel);
			if(r.meta.fileMeta[relPath]?.when)
				outputFile.setTS(r.meta.fileMeta[relPath]?.when.getTime());
		}

		for(const key of Object.keys(r.meta.fileMeta))
			delete r.meta.fileMeta[key].when;
	};
	renameOut = false;
}
