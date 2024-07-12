import {Format} from "../../Format.js";

export class lha extends Format
{
	name       = "LHArc Archive";
	website    = "http://fileformats.archiveteam.org/wiki/LHA";
	ext        = [".lha", ".lhz", ".lzs", ".exe", ".lzh", ".car"];
	idMeta     = ({macFileType}) => macFileType==="LHA ";

	// If it's a self-extracting archive, ensure it has a .exe extension
	safeExt = dexState => (dexState.hasMagics("LHA self-extracting") ? ".exe" : ".lha");

	magic = ["LHARC/LZARK compressed archive", /^LHa .*archive data/, "LHA File Format", "LHARK compressed archive", "LHA self-extracting", "LHarc self-extracting archive", "LZH Archiv gefunden", "CAR compressed archive", "Self-extracting Amiga LhA",
		"SDS Software SFX", /^LHarc .*archive data/, "LArc compressed archive", "Archive: LHA archive", /^MS-DOS .*LHarc self-extracting archive/, /^Self-extracting LZH$/, /^LZH$/, /^fmt\/626( |$)/];
	
	// Some files are 'LHARK' files that look almost identical to LHA files and can only be identified by trying them as lhark
	// Luckilly 'lha' fails on these, so then I try lhark specific extractor
	// See: https://entropymine.wordpress.com/2020/12/24/notes-on-lhark-compression-format/
	converters = ["lha", "sevenZip", "deark[module:lha][opt:lha:lhark]", "deark[module:car_lha] -> lha", "deark[module:lharc_sfx_com]", "unar", "sqc", "UniExtract[matchType:magic]", "izArc[matchType:magic]", "lhark", "uaeunp"];
}
