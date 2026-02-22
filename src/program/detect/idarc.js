import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {detectPreRename} from "../../dexUtil.js";
import {fileUtil} from "xutil";

export class idarc extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/IDArc";
	bin     = Program.binPath("idarc");
	loc     = "local";
	pre     = detectPreRename;
	args    = r => [r.detectTmpFilePath];
	post    = async r =>
	{
		await fileUtil.unlink(r.detectTmpFilePath);
		r.meta.detections = r.stdout.trim().split("\n").filter(v => !!v).map(line => Detection.create({value : `idarc: ${line.trim()}`, from : "idarc", file : r.f.input}));
	};
	renameOut = false;
}
