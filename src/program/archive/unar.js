import {Program, RUNTIME} from "../../Program.js";
import {encodeUtil, fileUtil} from "xutil";
import {path} from "std";

export class unar extends Program
{
	website   = "https://unarchiver.c3.cx/";
	package   = "app-arch/unar";
	flags   = {
		"mac"  : "Set this flag to treat the files extracted as mac files and rename them",
		"type" : "What type to process the file as. Kinda hacky, relies on this string being present at the end of the first line as : <type>"
	};
	bruteFlags = { executable : {} };

	bin      = "unar";
	args     = r => [...(r.flags.filenameEncoding ? ["-e", r.flags.filenameEncoding] : []), "-f", "-D", "-o", r.outDir(), r.inFile()];
	postExec = async r =>
	{
		if(!r.flags.mac)
			return;

		const decodeOpts = {processors : encodeUtil.macintoshProcessors.percentHex, region : RUNTIME.globalFlags?.osHint?.macintoshjp ? "japan" : "roman"};
		const outDirPath = r.outDir({absolute : true});
		const fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
		await fileOutputPaths.parallelMap(async fileOutputPath =>
		{
			const subPath = path.relative(outDirPath, fileOutputPath);
			const newSubPath = (await subPath.split("/").parallelMap(async v => await encodeUtil.decodeMacintosh({data : v, ...decodeOpts}))).join("/");
			if(subPath===newSubPath)
				return;
			
			// we have to mkdir and rename because some files like archive/sit/LOOPDELO.SIT have two different directories, one encoded one not encoded but when decoded they are equal
			await Deno.mkdir(path.join(outDirPath, path.dirname(newSubPath)), {recursive : true});
			await Deno.rename(path.join(outDirPath, subPath), path.join(outDirPath, newSubPath));
		});
	};
	verify = r => !r.flags.type || r.stdout?.trim()?.split("\n")?.[0]?.toLowerCase()?.endsWith(`: ${r.flags.type.toLowerCase()}`);
	renameOut = false;
}

