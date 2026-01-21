import {Format} from "../../Format.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class seventhLevelVideo extends Format
{
	name            = "7th Level Video";
	ext             = [".mov_data", ".mov_toc"];
	keepFilename    = true;
	auxFiles        = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));	// Both .mov_data and .mov_toc are required
	untouched       = ({f}) => f.input.ext.toLowerCase()===".mov_toc";	// Don't do anything with .mov_toc files
	verifyUntouched = false;
	pre             = async dexState =>
	{
		// copy over the parent palette file if it exists
		const paletteFilePath = path.resolve(dexState.original.input.dir, "..", "res0006");
		if(await fileUtil.exists(paletteFilePath))
			await Deno.copyFile(paletteFilePath, path.join(dexState.f.root, `res0006`));
	};
	converters = ["na_game_tool[format:7lev_movie]"];
}
