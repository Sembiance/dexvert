import {Format} from "../../Format.js";

export class multimediaViewerBook extends Format
{
	name       = "Multimedia Viewer Book";
	website    = "http://fileformats.archiveteam.org/wiki/Multimedia_Viewer_Book";
	ext        = [".mvb"];
	magic      = ["Multimedia Viewer Book"];
	converters = ["unHLPMVB[extractExtra]"];
}
