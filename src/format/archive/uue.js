import {Format} from "../../Format.js";

export class uue extends Format
{
	name       = "UU/XX Encoded Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Uuencoding";
	ext        = [".uue", ".uu"];
	magic      = ["uuencoded", "UUencoded", "UU-kodierte Datei", "xxencoded", "text/x-uuencode", "deark: uuencode (Uuencoded)", "deark: uuencode (Base64 with uuencode wrapper)", "deark: xxencode (XXEncoded)", /^fmt\/1102( |$)/];
	converters = ["uudecode", "deark[module:uuencode]", "deark[module:xxencode]", "sqc[strongMatch]", "izArc[strongMatch]", "UniExtract[strongMatch]"];
	verify     = ({inputFile, newFile}) => (newFile.size/inputFile.size)>=0.3 && newFile.size<inputFile.size;	// Output files should be smaller than input, so just a sanity check for any bad decodes
	notes      = "Haven't encountered may XX encoded files, those I have decode fine with uudecode. If find one that doesn't try using uudeview";
}
