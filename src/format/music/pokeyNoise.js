import {Format} from "../../Format.js";

export class pokeyNoise extends Format
{
	name         = "PokeyNoise Module";
	ext          = [".pn"];
	magic        = ["PokeyNoise chiptune"];
	keepFilename = true;

	auxFiles = (input, otherFiles) =>
	{
		// Can optionally use a .info file
		const otherFile = otherFiles.find(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.info`);
		return otherFile ? [otherFile] : false;
	};
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:Pokeynoise]"];
}
