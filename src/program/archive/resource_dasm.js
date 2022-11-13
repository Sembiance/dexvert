import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";
import {fileUtil, encodeUtil, runUtil} from "xutil";
import {path} from "std";

const FONT_SPRITE_COLS = 40;

export class resource_dasm extends Program
{
	website    = "https://github.com/fuzziqersoftware/resource_dasm";
	package    = "app-arch/resource-dasm";
	bin        = "resource_dasm";
	args       = r => ["--data-fork", r.inFile(), r.outDir()];
	runOptions = ({timeout : xu.MINUTE*10, killChildren : true});	// resource_dasm calls picttoppm which can hang (see sample archive/rsrc/Extend Demo ReadMe.rsrc)

	// If need to understand some resource types better: https://whitefiles.org/mac/pgs/t02.htm
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});

		let fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
		if(fileOutputPaths.length===0)
			return;

		// first remove the input filename prefix
		fileOutputPaths = await fileOutputPaths.parallelMap(async fileOutputPath =>
		{
			const filename = path.basename(fileOutputPath);
			const newFileOutputPath = path.join(path.dirname(fileOutputPath), filename.substring(path.basename(r.args[1]).length+1));
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
		for(const type of ["CODE"])
		{
			const typeFilePaths = fileOutputPaths.filter(v => path.basename(v).startsWith(`${type}_`) && v.endsWith(".txt"));
			if(!typeFilePaths.length)
				continue;

			for(const typeFilePath of typeFilePaths)
			{
				await fileUtil.unlink(typeFilePath);
				fileOutputPaths.removeOnce(typeFilePath);
			}
		}

		// for certain other text resource types, they are not very useful individually, so just combine into a single .txt file
		for(const type of ["ALRT", "CNTL", "DITL", "DLOG", "MENU", "WIND"])
		{
			const typeFilePaths = fileOutputPaths.filter(v => path.basename(v).startsWith(`${type}_`) && v.endsWith(".txt"));
			if(!typeFilePaths.length)
				continue;

			const typeCombinedFilePath = path.join(outDirPath, `${type}.txt`);
			for(const typeFilePath of typeFilePaths)
			{
				await Deno.writeTextFile(typeCombinedFilePath, `${path.basename(typeFilePath)}\n`, {append : true});
				await Deno.writeFile(typeCombinedFilePath, await Deno.readFile(typeFilePath), {append : true});
				await Deno.writeTextFile(typeCombinedFilePath, "\n\n", {append : true});
				await fileUtil.unlink(typeFilePath);
				fileOutputPaths.removeOnce(typeFilePath);
			}
		}

		// for fonts, every single glyph is a seperate file which generates huge numbers of files for Mac font CDs, so let's just combine all the glyphs together
		const fontGlyphs = {};
		for(const fileOutputPath of fileOutputPaths)
		{
			const {code, num, glyph} = path.basename(fileOutputPath).match(/(?<code>\w{4})_(?<num>-?\d+)_.*glyph_(?<glyph>\w+)\.bmp$/)?.groups || {};
			if(!code || !num || !glyph)
				continue;
			
			const fontid = `${code}_${num}`;
			fontGlyphs[fontid] ||= [];
			fontGlyphs[fontid].push(fileOutputPath);
		}

		await Object.entries(fontGlyphs).parallelMap(async ([fontid, filePaths]) =>
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
				await Deno.writeTextFile(textFilePath, "\n\n", {append : true});
			}
			await filePaths.parallelMap(async filePath =>
			{
				await fileUtil.unlink(filePath);
				fileOutputPaths.removeOnce(filePath);
			});
		});

		// all .bmp files, attempt to just quick convert using imagemagick. resources can have a ton of BMP files, this saves a lot of time further down the line and reduces duplication
		const bmpFilePaths = fileOutputPaths.filter(v => v.endsWith(".bmp"));
		await bmpFilePaths.parallelMap(async bmpFilePath =>
		{
			const pngFilePath = path.join(outDirPath, `${path.basename(bmpFilePath, ".bmp")}.png`);
			await runUtil.run("convert", [bmpFilePath, "-strip", "-define", "filename:literal=true", "-define", "png:exclude-chunks=time", pngFilePath], {timeout : xu.MINUTE});
			if(await fileUtil.exists(pngFilePath))
			{
				await fileUtil.unlink(bmpFilePath);
				fileOutputPaths.removeOnce(bmpFilePath);
			}
		}, 2);
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
