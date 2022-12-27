import {xu} from "xu";
import {Program, CONVERT_PNG_ARGS} from "../../Program.js";
import {fileUtil, runUtil, hashUtil, sysUtil} from "xutil";
import {path} from "std";

export class hypercard_dasm extends Program
{
	website   = "https://github.com/fuzziqersoftware/resource_dasm";
	package   = "app-arch/resource-dasm";
	bin       = "hypercard_dasm";
	args      = r => [r.inFile(), r.outDir()];

	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});

		const fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
		if(fileOutputPaths.length===0)
			return;

		// all .bmp files, just quick convert using imagemagick. hypercard_dasm producesa ton of BMP files, this saves a lot of time further down the line and reduces file duplication
		const bmpFilePaths = fileOutputPaths.filter(v => v.endsWith(".bmp"));
		const pngHashes = {};
		await bmpFilePaths.parallelMap(async bmpFilePath =>
		{
			const pngFilePath = path.join(outDirPath, `${path.basename(bmpFilePath, ".bmp")}.png`);
			await runUtil.run("convert", [bmpFilePath, ...CONVERT_PNG_ARGS, pngFilePath], {timeout : xu.MINUTE});
			if(await fileUtil.exists(pngFilePath))
			{
				await fileUtil.unlink(bmpFilePath);
				fileOutputPaths.removeOnce(bmpFilePath);
				
				// many times the card preview images produced are identical, so sum them here
				const hash = await hashUtil.hashFile("blake3", pngFilePath);
				pngHashes[hash] ||= [];
				pngHashes[hash].push(pngFilePath);
			}
		}, await sysUtil.optimalParallelism(bmpFilePaths.length));

		// now that we have all the hashes, we can remove any duplicate png files
		await Object.values(pngHashes).parallelMap(async pngFilePaths => await pngFilePaths.slice(1).parallelMap(fileUtil.unlink));
	};

	renameOut = false;
}
