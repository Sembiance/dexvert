import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";
import {path} from "std";

const STANDARD_BANK_FILE_PATHS = await fileUtil.tree(path.join(xu.dirname(import.meta), "..", "..", "..", "music", "rolBank"), {nodir : true});

export class rol extends Format
{
	name         = "AdLib/Roland Song";
	website      = "http://fileformats.archiveteam.org/wiki/AdLib_Visual_Composer_/_Roland_Synthesizer_song";
	ext          = [".rol"];
	magic        = ["AdLib Visual Composer music"];
	notes        = "Couldn't convert GIRLIPEN.ROL for some reason";
	keepFilename = true;

	auxFiles = (input, otherFiles, otherDirs) =>
	{
		const f = otherFiles.filter(otherFile => [".bnk", ".ins"].includes(otherFile.ext.toLowerCase()));
		const insDir = otherDirs.find(otherDir => otherDir.name.toLowerCase()==="ins");
		if(insDir)
			f.push(insDir);

		return f.length>0 ? f : false;
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
	metaProvider = ["musicInfo"];
	converters   = ["adplay", "rol2mus"];
}
