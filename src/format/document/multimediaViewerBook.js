import {Format} from "../../Format.js";

export class multimediaViewerBook extends Format
{
	name       = "Multimedia Viewer Book";
	website    = "http://fileformats.archiveteam.org/wiki/Multimedia_Viewer_Book";
	ext        = [".mvb", ".hlp"];
	weakExt    = [".hlp"];
	magic      = ["Multimedia Viewer Book", /^fmt\/1800( |$)/];
	converters = ["unHLPMVB[extractExtra]"];
}
