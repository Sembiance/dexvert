import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, encodeUtil} from "xutil";
import {path} from "std";

export class resource_dasm extends Program
{
	website    = "https://github.com/fuzziqersoftware/resource_dasm";
	package    = "app-arch/resource-dasm";
	bin        = "resource_dasm";
	args       = r => ["--data-fork", r.inFile(), r.outDir()];
	runOptions = ({timeout : xu.MINUTE*10, killChildren : true});	// resource_dasm calls picttoppm which can hang (see sample archive/rsrc/Extend Demo ReadMe.rsrc)

	postExec = async r =>
	{
		// resource_dasm will output any non-ascii MacOS Roman characters as URL encoded signs like %A5
		// Here we replace them with the proper unicode characters: https://en.wikipedia.org/wiki/Mac_OS_Roman
		const fileOutputPaths = await fileUtil.tree(r.outDir({absolute : true}), {nodir : true});
		if(fileOutputPaths.length===0)
			return;
		
		for(const fileOutputPath of fileOutputPaths)
		{
			const filename = path.basename(fileOutputPath);
			for(let i=0;i<encodeUtil.MACOS_ROMAN_EXTENDED.length;i++)
			{
				const hexCode = (i+0x80).toString(16).toUpperCase();	// resource_dasm seems to output capital hexadecimal letters
				if(!filename.includes(`%${hexCode}`))
					continue;
				
				await Deno.rename(fileOutputPath, path.join(path.dirname(fileOutputPath), filename.replaceAll(`%${hexCode}`, encodeUtil.MACOS_ROMAN_EXTENDED[i])));
			}
		}
	};

	renameOut = {
		alwaysRename : true,
		regex        : /^[^_]+_(?<resid>.{4})_(?<rest>.+)$/,	// this regex assumes the input filename doesn't have an underscore
		renamer      :
		[
			({suffix}, {resid, rest}) => [resid, "_", suffix, rest]
		]
	};
}
