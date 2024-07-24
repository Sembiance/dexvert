import {Format} from "../../Format.js";

export class uue extends Format
{
	name       = "UU/XX Encoded Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Uuencoding";
	ext        = [".uue", ".uu"];
	magic      = ["uuencoded", "UUencoded", "UU-kodierte Datei", "xxencoded", /^fmt\/1102( |$)/];
	notes      = "Haven't encountered may XX encoded files, those I have decode fine with uudecode. If find one that doesn't try using uudeview";
	converters = ["uudecode", "sqc", "izArc[matchType:magic]", "UniExtract[matchType:magic]"];
}
