import {Format} from "../../Format.js";
import {UInt8ArrayReader} from "UInt8ArrayReader";

export class ps2SaveIconModel extends Format
{
	name           = "Playstation 2 Save Icon Model";
	website        = "https://www.ps2savetools.com/documents/iconsys-format/";
	ext            = [".sys"];
	forbidExtMatch = true;
	idCheck        = inputFile => inputFile.size===964;
	magic          = ["PS2 Icon"];
	weakMagic      = true;
	auxFiles       = async (input, otherFiles, _otherDirs, {xlog}) =>
	{
		const reader = new UInt8ArrayReader(await Deno.readFile(input.absolute));
		const iconFilenames = [];
		reader.pos = 260;
		iconFilenames.pushUnique(reader.strTerminated());
		reader.pos = 324;
		iconFilenames.pushUnique(reader.strTerminated());
		reader.pos = 388;
		iconFilenames.pushUnique(reader.strTerminated());
		return otherFiles.filter(otherFile => iconFilenames.some(iconFilename => otherFile.base.toLowerCase()===iconFilename.toLowerCase()));
	};
	converters     = ["ico2gltf"];
}
