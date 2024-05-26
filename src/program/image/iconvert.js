import {xu} from "xu";
import {Program} from "../../Program.js";

export class iconvert extends Program
{
	website    = "https://github.com/AcademySoftwareFoundation/OpenImageIO";
	package    = "media-libs/openimageio";
	bin        = "iconvert";
	args       = async r => ["--threads", "1", r.inFile(), await r.outFile("out.png")];
	runOptions = ({timeout : xu.MINUTE}); // Can get hung up on certain files and just spin forever (image/jpeg2000/9tailhk0.jp2)
	renameOut  = true;
}
