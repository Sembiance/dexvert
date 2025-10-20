import {Format} from "../../Format.js";
import {_MACBINARY_MAGIC} from "../archive/macBinary.js";

export class lha extends Format
{
	name           = "LHArc Archive";
	website        = "http://fileformats.archiveteam.org/wiki/LHA";
	ext            = [".lha", ".lhz", ".lzs", ".exe", ".lzh", ".car", ".lz"];
	forbidExtMatch = [".exe"];
	idMeta         = ({macFileType}) => ["LARC", "LHA ", "LHA\0", "LHA□"].includes(macFileType);

	// If it's a self-extracting archive, ensure it has a .exe extension
	safeExt = dexState => (dexState.hasMagics("LHA self-extracting") ? ".exe" : ".lha");

	magic = [
		// generic LHA
		"LHARC/LZARK compressed archive", /^LHa .*archive data/, "LHA File Format", "LHARK compressed archive", "LHA self-extracting", "LHarc self-extracting archive", "LZH Archiv gefunden", "Self-extracting Amiga LhA", "application/x-lha",
		/^LHarc .*archive data/, "LArc compressed archive", "Archive: LHA archive", /^MS-DOS .*LHarc self-extracting archive/, /^Self-extracting LZH$/, /^LZH$/, "deark: lha", "deark: car_lha", /^LZH$/, /^fmt\/626( |$)/,

		// app specific LHA
		"Amiga WHDLoad package (lha compressed)", "CAR compressed archive", "SDS Software SFX", "Atari ST LHArc SFX archive"
	];
	
	// Some files are 'LHARK' files that look almost identical to LHA files and can only be identified by trying them as lhark
	// Luckilly 'lha' fails on these, so then I try lhark specific extractor
	// See: https://entropymine.wordpress.com/2020/12/24/notes-on-lhark-compression-format/
	converters = dexState => ["lha", "sevenZip", "deark[module:lha][opt:lha:lhark]", "deark[module:car_lha] -> lha", "deark[module:lharc_sfx_com]",
		dexState.hasMagics(_MACBINARY_MAGIC) ? "unar[mac]" : "unar",
		"sqc", "UniExtract[matchType:magic]", "izArc[matchType:magic]", "lhark", "uaeunp"
	];
}
