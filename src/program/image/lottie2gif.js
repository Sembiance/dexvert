import {xu} from "xu";
import {fileUtil} from "xutil";
import {Program} from "../../Program.js";

export class lottie2gif extends Program
{
	website = "https://github.com/Samsung/rlottie";
	package = "media-libs/rlottie";
	bin     = "lottie2gif";
	cwd     = r => r.outDir();
	args    = async r =>
	{
		const parsed = xu.parseJSON(await fileUtil.readTextFile(r.inFile({absolute : true})), {});
		const args = [r.inFile()];
		if(parsed.w && parsed.h)
			args.push(`${parsed.w}x${parsed.h}`);

		return args;
	};
	renameOut = true;
}

