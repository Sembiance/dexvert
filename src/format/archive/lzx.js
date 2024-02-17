import {Format} from "../../Format.js";
import {path} from "std";

export class lzx extends Format
{
	name       = "Lempel-Ziv Archive";
	website    = "http://fileformats.archiveteam.org/wiki/LZX";
	ext        = [".lzx"];
	magic      = ["LZX compressed archive", "LZX Amiga compressed archive", /^LZX$/];
	converters = ["unar", "unlzx", "UniExtract"];
	post = async dexState =>
	{
		await Object.entries(dexState.meta.fileProps).parallelMap(async ([filename, props]) =>
		{
			const outputFile = (dexState.f.files.output || []).find(file => file.absolute===path.join(dexState.f.outDir.absolute, filename));
			if(outputFile)
				await outputFile.setTS(props.ts);
		});
	};
	metaProvider = ["unlzx[listOnly]"];
}
