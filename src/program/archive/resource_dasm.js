import {xu} from "xu";
import {Program} from "../../Program.js";
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
		let fileOutputPaths = await fileUtil.tree(r.outDir({absolute : true}), {nodir : true});
		if(fileOutputPaths.length===0)
			return;

		fileOutputPaths = await fileOutputPaths.parallelMap(async fileOutputPath =>
		{
			const filename = path.basename(fileOutputPath);
			const newFileOutputPath = path.join(path.dirname(fileOutputPath), filename.substring(path.basename(r.args[1]).length+1));
			await Deno.rename(fileOutputPath, newFileOutputPath);
			return newFileOutputPath;
		});
		
		// resource_dasm will output any non-ascii MacOS Roman characters as URL encoded signs like %A5
		// Here we replace them with the proper unicode characters: https://en.wikipedia.org/wiki/Mac_OS_Roman
		fileOutputPaths = await fileOutputPaths.parallelMap(async fileOutputPath =>
		{
			let renamedFileOutputPath = fileOutputPath;

			for(let i=0;i<encodeUtil.MACOS_ROMAN_EXTENDED.length;i++)
			{
				const hexCode = (i+0x80).toString(16).toUpperCase();	// resource_dasm seems to output capital hexadecimal letters
				const filename = path.basename(renamedFileOutputPath);
				if(!filename.includes(`%${hexCode}`))
					continue;
				
				const newFileOutputPath = path.join(path.dirname(renamedFileOutputPath), filename.replaceAll(`%${hexCode}`, encodeUtil.MACOS_ROMAN_EXTENDED[i]));
				await Deno.rename(renamedFileOutputPath, newFileOutputPath);
				renamedFileOutputPath = newFileOutputPath;
			}

			return renamedFileOutputPath;
		});

		// for fonts, every single glyph is a seperate file which generates huge numbers of files for Mac font CDs, so let's just combine all the glyphs together
		const fontGlyphs = {};
		for(const fileOutputPath of fileOutputPaths)
		{
			const {code, num, glyph} = path.basename(fileOutputPath).match(/(?<code>\w{4})_(?<num>\d+)_glyph_(?<glyph>\w+)\.bmp$/)?.groups || {};
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
			await filePaths.parallelMap(fileUtil.unlink);
		});

		// for STR# resources, these are often tiny little files with just a few words. Let's combine them into a single .txt file
		const txtResources = {};
		for(const fileOutputPath of fileOutputPaths)
		{
			const {code, num, name} = path.basename(fileOutputPath).match(/(?<code>STR#)_(?<num>\d+)_(?<name>.+)\.txt$/)?.groups || {};
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
			await filePaths.parallelMap(fileUtil.unlink);
		});
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
