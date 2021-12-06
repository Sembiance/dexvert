import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";
import {path} from "std";

const STANDARD_BANK_FILE_PATHS = await fileUtil.tree(path.join(xu.dirname(import.meta), "..", "..", "..", "music", "rolBank"), {nodir : true});

export class rol extends Format
{
	name    = "AdLib/Roland Song";
	website = "http://fileformats.archiveteam.org/wiki/AdLib_Visual_Composer_/_Roland_Synthesizer_song";
	ext     = [".rol"];
	magic   = ["AdLib Visual Composer music"];
	notes   = "Couldn't convert GIRLIPEN.ROL for some reason";

	auxFiles = (input, otherFiles) =>
	{
		const bankFiles = otherFiles.filter(otherFile => otherFile.ext.toLowerCase()===".bnk");
		return bankFiles.length>0 ? bankFiles : false;
	};

	pre = async dexState =>
	{
		// Symlink to our standard bank files
		await STANDARD_BANK_FILE_PATHS.parallelMap(async bankFilePath =>
		{
			const destBankFilePath = path.join(dexState.f.root, path.basename(bankFilePath).toLowerCase());
			if(await fileUtil.exists(destBankFilePath))
				return;

			await Deno.symlink(bankFilePath, destBankFilePath);
		});
	};
	converters = ["adplay"];
}
