import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class lottie extends Format
{
	name         = "Lottie";
	website      = "https://github.com/Samsung/rlottie";
	ext          = [".json"];
	mimeType     = "application/json";
	keepFilename = true;
	notes        = "Will only match lottie files that include a layers property.";

	// abydosconvert also supports this format, unfortuantely as of abydos-0.2.4 it currently doesn't animate correctly, not clearing canvas between frames
	// So we just use lottie2gif instead which is included in rlottie
	converters = ["lottie2gif"]

	auxFiles = async (inputFile, otherFiles, otherDirs) =>
	{
		// Some lottie files include image assets
		const parsed = xu.parseJSON(await fileUtil.readFile(inputFile.absolute), {});
		if(!parsed || !parsed.assets)
			return false;
		
		const a = [];
		for(const asset of parsed.assets)
		{
			if(!asset.u || !asset.p)
				continue;

			const subPath = path.join(asset.u, asset.p);
			if(subPath.includes("/"))
				a.push(...otherDirs.filter(otherDir => otherDir.base===subPath.split("/")[0]));
			else
				a.push(...otherFiles.filter(otherFile => otherFile.base===subPath));
		}

		return a.length>0 ? a : false;
	};

	idCheck = async inputFile => !!xu.parseJSON(await fileUtil.readFile(inputFile.absolute))?.layers;
}
