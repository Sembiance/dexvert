import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class ilbm2frames extends Program
{
	website    = "https://github.com/Sembiance/ilbm2frames";
	package    = "media-gfx/ilbm2frames";
	unsafe     = true;
	//bin        = "/mnt/compendium/DevLab/apps/ilbm2frames/ilbm2frames";
	bin        = "ilbm2frames";
	runOptions = ({virtualX : true});
	args       = r => ["--fps", "20", "--limitSeconds", "5", r.inFile(), r.outDir()];
	postExec   = async r =>
	{
		const data = xu.parseJSON(r.stdout);
		let keepFrames = true;
		// check to see we have image data JSON. If we don't it's possible we segfaulted, but nothing I can do about that and the image was unlikely to have produced good frames anyways
		if(!data || !data.imageCount || !data.images?.length || !data.images[0])
		{
			keepFrames = false;
		}
		else
		{
			// now time to do some more advanced checks of the color cycling values to try and 'detect' stale images or flashy/spazzy images
			const o = data.images[0];
			const ranges = [...(o.colorRanges || []), ...(o.dRanges || [])];

			// if any of our range rates are less than zero, or if we don't have any ===0 or >200, or all are rate 0 then don't keep our frames
			if(ranges.length>0 && (ranges.some(({rate}) => rate<0) || !ranges.some(({rate}) => rate===0 || rate>200) || ranges.every(({rate}) => rate===0)))
				keepFrames = false;
			
			// additional stale checks
			if(keepFrames && (o.colorRanges || []).length>0)
			{
				const distances = o.colorRanges.map(({low, high}) => Math.abs(high-low));
				if(distances.average()<=0.2 || Object.values(distances).standardDeviation()>=1000 || Object.values(distances).average()<=0.3 || (distances.variance()===0 && o.colorRanges?.length===1 && !o.dRanges?.length))
					keepFrames = false;
			}

			// additional spaz checks
			if(keepFrames && (o.colorRanges || []).map(({pad1}) => pad1).average()<0)
				keepFrames = false;
		}

		if(keepFrames)
			return;
		
		await (await fileUtil.tree(r.outDir({absolute : true}), {regex : /\.bmp$/, nodir : true})).parallelMap(async frameFilePath => await fileUtil.unlink(frameFilePath));
	};
	renameOut  = false;
}
