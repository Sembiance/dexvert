import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil, imageUtil} from "xutil";
import * as path from "https://deno.land/std@0.114.0/path/mod.ts";
import { parse as xmlParse } from "https://deno.land/x/xml@v1.0.2/mod.ts";

export class svgInfo extends Program
{
	website       = "https://github.com/Sembiance/dexvert/bin/svgInfo.js";

	exec = async r =>
	{
		// convert to PNG to get color count and opaque info
		const pngFilePath = await fileUtil.genTempPath(r.f.root, ".png");
		await runUtil.run("resvg", ["--width", "500", r.f.input.rel, path.relative(r.f.root, pngFilePath)], {cwd : r.f.root, verbose : xu.verbose>=3});
		const imageInfo = await imageUtil.getInfo(pngFilePath, {timeout : xu.SECOND*30});
		await Deno.remove(pngFilePath);

		if(imageInfo.opaque || imageInfo.colorCount>1)
		{
			r.meta.opaque = imageInfo.opaque;
			r.meta.colorCount = imageInfo.colorCount;
		}

		if(r.f.input.size<xu.MB*30)
		{
			// our xml parser chokes on some input files, like test/sample/image/svg/abydos.svg
			// so we run them through svgo first which seems to produce saner XML output that works with out xml parser
			const fixedSVGFilePath = await fileUtil.genTempPath(r.f.root, ".svg");
			await runUtil.run("svgo", ["--output", fixedSVGFilePath, "--input", r.f.input.rel], {cwd : r.f.root, verbose : xu.verbose>=3});
			
			const svgData = xmlParse(await fileUtil.readFile(fixedSVGFilePath));
			await Deno.remove(fixedSVGFilePath);

			if(!svgData || !svgData.svg || Object.keys(svgData.svg).filter(k => !k.startsWith("@")).length===0)
			{
				// If we have no children, doesn't matter if width/height/viewBox is set, there isn't anything to draw
				Object.assign(r.meta, {width : 0, height : 0});
			}
			else if(svgData.svg?.["@width"] && svgData.svg?.["@height"])
			{
				Object.assign(r.meta, {width : +svgData.svg["@width"].toString().match(/\d+/)[0], height : +svgData.svg["@height"].toString().match(/\d+/)[0]});
			}
			else if(svgData.svg?.["@viewBox"])
			{
				const [x, y, width, height] = svgData.svg["@viewBox"].split(" ").map(v => +v);
				Object.assign(r.meta, {width : width-x, height : height-y});
			}
			else
			{
				Object.assign(r.meta, {width : 0, height : 0});
			}
		}
	}
}
