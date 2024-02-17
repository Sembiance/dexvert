import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";
import {encodeUtil, fileUtil, runUtil} from "xutil";
import {path} from "std";

export class unar extends Program
{
	website = "https://github.com/incbee/Unarchiver";
	package = "app-arch/unar";
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
		let fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
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
		
		r.meta.fileMeta = {};

		const num2str = num =>
		{
			const u8arr = new Uint8Array(4);
			u8arr.setUInt32BE(0, num);
			return u8arr.getString(0, 4);
		};

		// Get our file creator types for better detection of extracted files down the line
		fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
		const {stdout : fileInfoRaw} = await runUtil.run("lsar", ["--json", r.inFile({absolute : true})]);
		for(const fileInfo of xu.parseJSON(fileInfoRaw)?.lsarContents || [])
		{
			if(!fileInfo.XADFileCreator || !fileInfo.XADFileName || fileInfo.XADIsResourceFork)
				continue;
				
			const fileOutputPath = fileOutputPaths.find(v => path.relative(outDirPath, v)===fileInfo.XADFileName);
			if(!fileOutputPath)
				continue;
			
			r.meta.fileMeta[fileInfo.XADFileName] = { macFileType : num2str(fileInfo.XADFileType), macFileCreator : num2str(fileInfo.XADFileCreator) };
		}

		if(Object.keys(r.meta.fileMeta).length===0)
			delete r.meta.fileMeta;
	};
	post = r =>
	{
		if(r.stdout.includes("This archive requires a password to unpack"))
			r.meta.passwordProtected = true;
	};
	verify    = r => !r.flags.type || r.stdout?.trim()?.split("\n")?.[0]?.toLowerCase()?.endsWith(`: ${r.flags.type.toLowerCase()}`);
	renameOut = false;
}

