import {Format} from "../../Format.js";

export class lha extends Format
{
	name       = "LHArc Archive";
	website    = "http://fileformats.archiveteam.org/wiki/LHA";
	ext        = [".lha", ".lhz", ".lzs", ".exe"];

	// If it's a self-extracting archive, ensure it has a .exe extension
	safeExt = dexState => (dexState.ids.some(id => id.magic.startsWith("LHA self-extracting")) ? ".exe" : ".lha");

	magic = ["LHARC/LZARK compressed archive", /^LHa .*archive data/, "LHA File Format", "LHA self-extracting", "LHarc self-extracting archive", /^LHarc .*archive data/, "LArc compressed archive"];
	
	// Some files are 'LHARK' files that look almost identical to LHA files and can only be identified by trying them as lhark
	// Luckilly 'lha' fails on these, so then I try lhark specific extractor
	// See: https://entropymine.wordpress.com/2020/12/24/notes-on-lhark-compression-format/
	converters = ["lha", "sevenZip", "deark[opt:lha:lhark]", "UniExtract[matchType:magic]", "lhark"];	// NOTE: The lhark extractor doesn't preserve timestamps, which is why it's last on the list
}
