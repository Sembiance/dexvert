import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil, imageUtil} from "xutil";
import {path} from "std";
import {xmlParse} from "denoLandX";

export class svgInfo extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	exec    = async r =>
	{
		// convert to PNG to get color count and opaque info
		const pngFilePath = await fileUtil.genTempPath(r.f.root, ".png");
		await runUtil.run("resvg", ["--width", "500", r.inFile(), path.relative(r.f.root, pngFilePath)], {cwd : r.f.root});
		const imageInfo = await imageUtil.getInfo(pngFilePath, {timeout : xu.SECOND*30});
		await fileUtil.unlink(pngFilePath);

		r.meta.opaque = imageInfo.opaque;
		r.meta.colorCount = imageInfo.colorCount;

		if(r.f.input.size<xu.MB*30)
		{
			const svgData = xmlParse(await Deno.readTextFile(r.inFile({absolute : true})));
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
	};
	renameOut = false;
}
