import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";
import {encodeUtil, fileUtil, runUtil} from "xutil";
import {path} from "std";

export class unar extends Program
{
	website = "https://github.com/incbee/Unarchiver";
	package = "app-arch/unar";
	flags   = {
		"mac"                     : "Set this flag to treat the files extracted as mac files and rename them",
		"type"                    : "What type to process the file as. Kinda hacky, relies on this string being present as: ': <type>'",
		"skipMacBinaryConversion" : "Set this flag to skip the macbinary conversion step",
		"allowFailedParsing"      : "Set this flag to allow unar to continue even if it reports that archive parsing failed"
	};
	bruteFlags = { executable : {} };

	bin  = "unar";
	args = async r =>
	{
		const {stdout : fileInfoRaw} = await runUtil.run("lsar", ["-json", r.inFile({absolute : true})]);
		r.lsarOutput = xu.parseJSON(fileInfoRaw);

		//if(!r.flags.mac && r.lsarOutput?.lsarFormatName==="MacBinary")
		//	r.flags.mac = true;

		const a = [];
		let encoding = r.flags.filenameEncoding;	// if we specified an ecoding, use it
		if(!encoding && r.flags.mac && RUNTIME.globalFlags?.osHint?.macintoshjp && !["macintosh", "UTF-8"].includes(r.lsarOutput?.lsarEncoding))	// otherwise if we are hinted as macintoshjp, use that so long as lsar didn't detect macintosh or UTF-8 (sample sea/まきがめ駒○駒BY彦ぷん)
			encoding = "x-mac-japanese";
		if(encoding)
			a.push("-e", encoding);

		a.push("-f", "-D", "-o", r.outDir(), r.inFile());
		return a;
	};
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		if(!r.flags.allowFailedParsing && r.stdout.includes("Archive parsing failed!"))	// otherwise things like exe/gws.exe will incorrectly be extracted as an archive/arc file
		{
			r.xlog.info`unar Archive parsing failed! Not safe to keep files! Deleting output files!`;
			await fileUtil.unlink(outDirPath, {recursive : true});
			await Deno.mkdir(outDirPath);
			return;
		}

		// For some files (archive/arArchive/STRMBASE.LIB) unar will produce massively deep directories. We make sure out paths are not too long (4096, but since that's total path, we use a lower amount, 3840)
		const longPaths = (await fileUtil.tree(outDirPath, {relative : true})).filter(v => v.length>3840).sortMulti([v => v.length], [false]);
		for(const longPath of longPaths)
		{
			const fullLongPath = path.join(outDirPath, longPath);
			r.xlog.debug`Deleting too long path: ${fullLongPath}`;
			await runUtil.run("rm", ["-rf", fullLongPath]);	// have to use rm here because fileUtil.unlink/Deno.remove doesn't work on too long paths
		}

		if(!r.flags.mac)
			return;

		const region = RUNTIME.globalFlags?.osHint?.macintoshjp ? "japan" : "roman";

		const decodeOpts = {processors : encodeUtil.macintoshProcessors.percentHex, region};
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

		if(!r.flags.skipMacBinaryConversion)
		{
			// NOTE: We can't rely on this entirely because sometimes files appear as somethign else (archive/diskDoubler) but when passed to unar it extracts as a macbinary file, so the script below actually double-checks we don't create the same thing over and over
			fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true, regex : /\.rsrc$/});
			await fileOutputPaths.parallelMap(async fileOutputPath => await runUtil.run("deno", runUtil.denoArgs(Program.binPath("appleDouble2MacBinary2.js"), `--originalFilePath=${r.inFile({absolute : true})}`, `--region=${region}`, fileOutputPath), runUtil.denoRunOpts()), 6);
		}
		
		r.meta.fileMeta = {};

		const num2str = async num =>
		{
			const u8arr = new Uint8Array(4);
			u8arr.setUInt32BE(0, num);
			
			// Used to us u8arr.getString(0, 4) here but that wasn't properly decoding the extended mac charset
			// We force roman region since that's all type/creator codes can be
			return await encodeUtil.decodeMacintosh({data : [0, 1, 2, 3].map(v => `%${u8arr.getUInt8(v).toString(16).padStart(2, "0")}`).join(""), processors : encodeUtil.macintoshProcessors.percentHex, region : "roman"});
		};

		// Get our file creator types for better detection of extracted files down the line
		fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
		for(const fileInfo of r.lsarOutput?.lsarContents || [])
		{
			if(!fileInfo.XADFileCreator || !fileInfo.XADFileName)
				continue;
			
			const fileRelPath = `${await encodeUtil.decodeMacintosh({data : fileInfo.XADFileName, ...decodeOpts})}${fileInfo.XADIsResourceFork ? ".rsrc" : ""}`;
			const fileOutputPath = fileOutputPaths.find(v => path.relative(outDirPath, v)===fileRelPath);
			if(!fileOutputPath)
				continue;

			r.meta.fileMeta[fileRelPath] = { macFileType : await num2str(fileInfo.XADFileType), macFileCreator : await num2str(fileInfo.XADFileCreator) };
		}

		if(Object.keys(r.meta.fileMeta).length===0)
			delete r.meta.fileMeta;
	};
	post = r =>
	{
		if(r.stdout.includes("This archive requires a password to unpack"))
			r.meta.passwordProtected = true;
	};
	verify    = r => !r.flags.type || r.stdout?.trim()?.split("\n")?.[0]?.toLowerCase()?.includes(`: ${r.flags.type.toLowerCase()}`);
	renameOut = false;
}

