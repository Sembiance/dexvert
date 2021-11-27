import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class lottie2gif extends Program
{
	website       = "https://github.com/Samsung/rlottie";
	gentooPackage = "media-libs/rlottie";
	bin           = "lottie2gif";
	cwd           = r => r.outDir();
	args          = async r =>
	{
		const parsed = xu.parseJSON(await fileUtil.readFile(r.inFile({absolute : true})), {});
		const args = [r.inFile()];
		if(parsed.w && parsed.h)
			args.push(`${parsed.w}x${parsed.h}`);

		return args;
	};
}

