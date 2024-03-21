import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";
import {fileUtil, encodeUtil, runUtil} from "xutil";
import {path} from "std";
import {quickConvertImages} from "../../dexUtil.js";

const FONT_SPRITE_COLS = 40;

export class resource_dasm extends Program
{
	website = "https://github.com/fuzziqersoftware/resource_dasm";
	package = "app-arch/resource-dasm";
	bin     = "resource_dasm";
	args    = r => ["--skip-external-decoders", "--image-format=png", "--data-fork", r.inFile(), r.outDir()];

	// If need to understand some resource types better: https://whitefiles.org/mac/pgs/t02.htm
	// Also: https://github.com/fuzziqersoftware/resource_dasm/blob/master/README.md
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});

		let fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
		if(fileOutputPaths.length===0)
			return;

		// first remove the input filename prefix and any .bin extensions (so we don't it later)
		fileOutputPaths = await fileOutputPaths.parallelMap(async fileOutputPath =>
		{
			const filename = path.basename(fileOutputPath);
			const newFileOutputPath = path.join(path.dirname(fileOutputPath), filename.substring(path.basename(r.args.at(-2)).length+1));
			await Deno.rename(fileOutputPath, newFileOutputPath);
			return newFileOutputPath;
		});
		
		// resource_dasm will output any non-ascii MacOS Roman characters as URL encoded signs like %A5
		// Here we replace them with the proper unicode characters: https://en.wikipedia.org/wiki/Mac_OS_Roman
		const decodeOpts = {processors : encodeUtil.macintoshProcessors.percentHex, region : RUNTIME.globalFlags?.osHint?.macintoshjp ? "japan" : "roman"};
		fileOutputPaths = await fileOutputPaths.parallelMap(async fileOutputPath =>
		{
			const subPath = path.relative(outDirPath, fileOutputPath);
			const newSubPath = (await subPath.split("/").parallelMap(async v => await encodeUtil.decodeMacintosh({data : v, ...decodeOpts}))).join("/");
			if(subPath===newSubPath)
				return fileOutputPath;
			
			// we have to mkdir and rename because some files like archive/sit/LOOPDELO.SIT have two different directories, one encoded one not encoded but when decoded they are equal
			await Deno.mkdir(path.join(outDirPath, path.dirname(newSubPath)), {recursive : true});
			await Deno.rename(path.join(outDirPath, subPath), path.join(outDirPath, newSubPath));

			return path.join(outDirPath, newSubPath);
		});

		// some file types are not interesting, delete them
		const removeRegexes =
		[
			// Just code dumps
			...["ADBS", "adio", "AINI", "atlk", "boot", "CDEF", "cdek", "cdev", "cfrg", "citt", "clok", "cmtb", "cmu!", "CODE", "code", "dcmp", "dcod", "dem ", "dimg", "drvr", "DRVR", "enet", "epch", "expt", "FKEY", "fovr", "gcko", "gdef", "GDEF", "gnld", "INIT", "krnl", "LDEF", "lmgr", "lodr", "ltlk", "MBDF", "MDEF", "mntr", "ncmp", "ndlc", "ndmc", "ndrv", "nift", "nitt", "nlib", "nsnd", "nsrd", "ntrb", "osl ", "otdr", "otlm", "PACK", "pnll", "ppct", "proc", "PTCH", "ptch", "pthg", "qtcm", "ROvr", "RSSC", "scal", "scod", "SERD", "sfvr", "shal", "sift", "SMOD", "snth", "tdig", "tokn", "vdig", "wart", "WDEF", "XCMD", "XFCN"].map(v => new RegExp(`^${v}_.+\\.txt$`)),

			// Just font information, kerning, etc, not particularly useful
			/^FONT_.+_description\.txt$/,

			// Usually a .png is produced as well
			/^(actb|cctb|clut|dctb|fctb|pltt|wctb)_.+\.(act|bin)$/,
			/^(icl[48]|ICN#|ics[48#])_.+\.icns$/
		];
		for(const regex of removeRegexes)
		{
			const typeFilePaths = fileOutputPaths.filter(v => regex.test(path.basename(v)));
			if(!typeFilePaths.length)
				continue;

			for(const typeFilePath of typeFilePaths)
			{
				await fileUtil.unlink(typeFilePath);
				fileOutputPaths.removeOnce(typeFilePath);
			}
		}

		// for certain other text resource types, they are not very useful individually, so just combine into a single .txt file
		for(const type of ["ALRT", "BNDL", "CNTL", "DITL", "DLOG", "FREF", "MENU", "TMPL", "TYP#", "WIND"])
		{
			const typeFilePaths = fileOutputPaths.filter(v => path.basename(v).startsWith(`${type}_`) && v.endsWith(".txt"));
			if(!typeFilePaths.length)
				continue;

			const typeCombinedFilePath = path.join(outDirPath, `${type}.txt`);
			for(const typeFilePath of typeFilePaths)
			{
				await fileUtil.writeTextFile(typeCombinedFilePath, `${path.basename(typeFilePath)}\n`, {append : true});
				await Deno.writeFile(typeCombinedFilePath, await Deno.readFile(typeFilePath), {append : true});
				await fileUtil.writeTextFile(typeCombinedFilePath, "\n\n", {append : true});
				await fileUtil.unlink(typeFilePath);
				fileOutputPaths.removeOnce(typeFilePath);
			}
		}

		// icons that have a merged composite, delete the other versions
		const filePathsToRemove = new Set();
		const filePathsToAdd = [];
		await fileOutputPaths.filter(v => v.includes("_composite.")).parallelMap(async compositeFilePath =>
		{
			const iconPrefix = path.basename(compositeFilePath).split("_composite.")[0].replace(/^(?<code>\w{4})_(?<num>-?\d+)_.+$/, "$1_$2");
			for(const filePath of fileOutputPaths)
			{
				const filename = path.basename(filePath);
				if(!filename.includes("_composite.") && filename.startsWith(iconPrefix))
					filePathsToRemove.add(filePath);
			}

			const newFilePath = compositeFilePath.replace("_composite.", ".");
			await Deno.rename(compositeFilePath, newFilePath);
			fileOutputPaths.removeOnce(compositeFilePath);
			filePathsToAdd.push(newFilePath);
		});
		fileOutputPaths.push(...filePathsToAdd);
		await Array.from(filePathsToRemove.values()).parallelMap(async filePath =>
		{
			await fileUtil.unlink(filePath);
			fileOutputPaths.removeOnce(filePath);
		});

		// some images, like font glyphs, PAT#, etc should be be combined together into a single image file
		const combineRegexes =
		[
			/^(?<code>\w{4})_(?<num>-?\d+)_.*glyph_\w+\.png$/,
			/^(?<code>icns|ic[ms][48#])_(?<num>-?\d+)_.+\.png$/,
			/^(?<code>(PAT#|SICN))_(?<num>-?\d+)_.+\.png$/
		];
		for(const regex of combineRegexes)
		{
			const subImages = {};
			for(const fileOutputPath of fileOutputPaths)
			{
				const {code, num} = path.basename(fileOutputPath).match(regex)?.groups || {};
				if(!code || !num)
					continue;
				
				const imageid = `${code}_${num}`;
				subImages[imageid] ||= [];
				subImages[imageid].push(fileOutputPath);
			}

			await Object.entries(subImages).parallelMap(async ([fontid, filePaths]) =>
			{
				const cols = Math.min(filePaths.length, FONT_SPRITE_COLS);
				const rows = Math.ceil(filePaths.length/FONT_SPRITE_COLS);
				await runUtil.run("montage", [...filePaths, "-tile", `${cols}x${rows}`, "-geometry", "+0+0", path.join(r.outDir({absolute : true}), `${fontid}.png`)], {timeout : xu.MINUTE*2});
				await filePaths.parallelMap(async filePath =>
				{
					await fileUtil.unlink(filePath);
					fileOutputPaths.removeOnce(filePath);
				});
			});
		}

		// for STR# resources, these are often tiny little files with just a few words. Let's combine them into a single .txt files while preserving their id numbers
		const txtResources = {};
		for(const fileOutputPath of fileOutputPaths)
		{
			const {code, num, name} = path.basename(fileOutputPath).match(/(?<code>STR#)_(?<num>-?\d+)_(?<name>.+)\.txt$/)?.groups || {};
			if(!code || !num || !name)
				continue;

			const textid = `${code}_${num}`;
			txtResources[textid] ||= [];
			txtResources[textid].push(fileOutputPath);
		}

		await Object.entries(txtResources).parallelMap(async ([textid, filePaths]) =>
		{
			const textFilePath = path.join(r.outDir({absolute : true}), `${textid}.txt`);
			for(const filePath of filePaths)
			{
				await Deno.writeFile(textFilePath, await Deno.readFile(filePath), {append : true});
				await fileUtil.writeTextFile(textFilePath, "\n\n", {append : true});
			}
			await filePaths.parallelMap(async filePath =>
			{
				await fileUtil.unlink(filePath);
				fileOutputPaths.removeOnce(filePath);
			});
		});

		await quickConvertImages(r, fileOutputPaths);

		// finally any .bin files left, drop the .bin extension
		await (await fileUtil.tree(outDirPath, {nodir : true, regex : /\.bin$/})).parallelMap(async fileOutputPath => await Deno.rename(fileOutputPath, fileOutputPath.substring(0, fileOutputPath.length-4)));
	};

	renameOut = {
		alwaysRename : true,
		regex        : /^.+_(?<resid>.{4})_(?<rest>.+)$/,	// this regex assumes the input filename doesn't have an underscore
		renamer      :
		[
			({suffix}, {resid, rest}) => [resid, "_", suffix, rest]
		]
	};
}
