import {xu} from "xu";
import {Program} from "../../Program.js";

export class montage extends Program
{
	website   = "https://www.imagemagick.org/";
	package   = "media-gfx/imagemagick";
	bin       = "montage";
	flags        = {
		colCount : "Number of columns in the output image. Default is 20."
	};
	args      = async r => [...r.inFiles(), "-tile", `${Math.min(r.inFiles().length, (+(r.flags.colCount || 20)))}x${Math.ceil(r.inFiles().length/ (+(r.flags.colCount || 20)))}`, "-geometry", "+0+0", await r.outFile(`out.png`)];
	renameOut = true;
}

/*
await Object.entries(subImages).parallelMap(async ([tileid, filePaths]) =>
		{
			const cols = ;
			const rows = ;
			await runUtil.run("montage", [...filePaths.sortMulti([([num]) => num]).map(([, filePath]) => filePath), "-tile", `${cols}x${rows}`, "-geometry", "+0+0", path.join(r.outDir({absolute : true}), `${tileid}.png`)], {timeout : xu.MINUTE*2});
			await filePaths.parallelMap(async ([, filePath]) =>
			{
				await fileUtil.unlink(filePath);
				fileOutputPaths.removeOnce(filePath);
			});
		});
		*/