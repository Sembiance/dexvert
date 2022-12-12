import {xu} from "xu";
import {fileUtil} from "xutil";
import {Format} from "../../Format.js";
import {path} from "std";

export class lottie extends Format
{
	name         = "Lottie";
	website      = "https://github.com/Samsung/rlottie";
	ext          = [".json"];
	mimeType     = "image/x-lottie+json";
	keepFilename = true;
	notes        = "Will only match lottie files that include a layers property.";
	converters   = ["lottie2gif", `abydosconvert[format:${this.mimeType}]`];

	auxFiles = async (inputFile, otherFiles, otherDirs) =>
	{
		// Some lottie files include image assets
		const parsed = xu.parseJSON(await fileUtil.readTextFile(inputFile.absolute), {});
		if(!parsed?.assets)
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

	idCheck = async inputFile => inputFile.size<xu.MB*20 && !!xu.parseJSON(await fileUtil.readTextFile(inputFile.absolute))?.layers;
}
