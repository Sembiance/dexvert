import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil, runUtil} from "xutil";

const PAT_SPRITE_COLS = 20;

export class stackimport extends Program
{
	website       = "https://github.com/uliwitness/stackimport/";
	package       = "dev-util/stackimport";
	bin           = "stackimport";
	args          = r => [r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	postExec      = async r =>
	{
		const outDirPath = r.outDir({absolute : true});

		const fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
		if(fileOutputPaths.length===0)
			return;

		const patPBMFilePaths = [];
		const otherPBMFilePaths = [];

		// combine card_*.xml files into one cards.xml file
		const cardsXMLFilePath = path.join(outDirPath, "cards.xml");
		for(const fileOutputPath of Array.from(fileOutputPaths))
		{
			const filename = path.basename(fileOutputPath);
			
			if((/^card_-?\d+\.xml$/).test(filename))
			{
				// if we have a corresponding .txt file from deark (I like the format better) then just delete this one
				// we often don't though as deark crashes on lots of different hypercard files
				if(fileOutputPaths.some(v => path.basename(v)===`${filename.slice(0, -3)}.txt`))
				{
					await fileUtil.unlink(fileOutputPath);
					continue;
				}
				
				// otherwise, combine the little card_*.xml files into one big cards.xml file
				await Deno.writeTextFile(cardsXMLFilePath, `${filename}\n`, {append : true});
				await Deno.writeFile(cardsXMLFilePath, await Deno.readFile(fileOutputPath), {append : true});
				await Deno.writeTextFile(cardsXMLFilePath, "\n\n", {append : true});
				await fileUtil.unlink(fileOutputPath);
				continue;
			}

			// if we are a PAT file, add it to an array for later combining and removal
			if((/^PAT_-?\d+.pbm$/).test(filename))
			{
				patPBMFilePaths.push(fileOutputPath);
				continue;
			}
			else if(filename.toLowerCase().endsWith(".pbm"))
			{
				otherPBMFilePaths.push(fileOutputPath);
				continue;
			}

			if(path.relative(outDirPath, fileOutputPath).split("/").length===2)
				await Deno.rename(fileOutputPath, path.join(outDirPath, filename));
		}

		// WARNING: Do not attempt to use fileOutputPaths below here, it no longer is correct due to the renaming operation above

		// for PAT files, they are so tiny and insignificant and almost always identical for every hypercard stack, just combine them into a big PAT file
		if(patPBMFilePaths.length>0)
		{
			const cols = Math.min(patPBMFilePaths.length, PAT_SPRITE_COLS);
			const rows = Math.ceil(patPBMFilePaths.length/PAT_SPRITE_COLS);
			await runUtil.run("montage", [...patPBMFilePaths, "-tile", `${cols}x${rows}`, "-geometry", "+0+0", path.join(outDirPath, `PATs.png`)], {timeout : xu.MINUTE*2});
			await patPBMFilePaths.parallelMap(fileUtil.unlink);
		}

		// convert all remaining .pbm files to .png with imagemagick
		await otherPBMFilePaths.parallelMap(async imageFilePath =>
		{
			const pngFilePath = path.join(outDirPath, `${path.basename(imageFilePath, ".pbm")}.png`);
			await runUtil.run("convert", [imageFilePath, "-strip", "-define", "filename:literal=true", "-define", "png:exclude-chunks=time", pngFilePath], {timeout : xu.MINUTE});
			if(await fileUtil.exists(pngFilePath))
				await fileUtil.unlink(imageFilePath);
		}, 2);
	};
	renameOut = false;
}
