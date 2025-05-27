import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil, imageUtil} from "xutil";
import {path} from "std";
import {xmlParse} from "denoLandX";

export class svgInfo extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	package = "media-libs/resvg";
	exec    = async r =>
	{
		let imageInfo;
		try
		{
			// convert to PNG to get color count and opaque info
			const pngFilePath = await fileUtil.genTempPath(r.f.root, ".png");
			await runUtil.run("resvg", ["--width", "500", r.inFile(), path.relative(r.f.root, pngFilePath)], {timeout : xu.MINUTE*2, cwd : r.f.root});
			imageInfo = await imageUtil.getInfo(pngFilePath, {timeout : xu.SECOND*30});
			await fileUtil.unlink(pngFilePath);
			r.meta.opaque = imageInfo.opaque;
			r.meta.colorCount = imageInfo.colorCount;
		}
		catch {}

		if(r.f.input.size<xu.MB*30)
		{
			try
			{
				const svgData = xmlParse(await fileUtil.readTextFile(r.inFile({absolute : true})));
				if(!svgData?.svg || Object.keys(svgData.svg).filter(k => !k.startsWith("@")).length===0)
				{
					// If we have no children, doesn't matter if width/height/viewBox is set, there isn't anything to draw
					Object.assign(r.meta, {width : 0, height : 0});
				}
				else if(svgData.svg?.["@width"] && svgData.svg?.["@height"])
				{
					for(const dim of ["width", "height"])
					{
						const {dimRawValue, dimUnit} = (/(?<dimRawValue>[\d.]+)(?<dimUnit>.+)?/).exec(svgData.svg[`@${dim}`].toString())?.groups || {};
						r.meta[dim] = Math.round((+dimRawValue) * ({mm : 3.7795275591, cm : 37.795275591, in : 96, pt : 1.3333333333, pc : 16.9333333333, px : 1}[dimUnit || "px"]) || 1);	// eslint-disable-line unicorn/numeric-separators-style
					}
				}
				else if(svgData.svg?.["@viewBox"])
				{
					const [x, y, width, height] = svgData.svg["@viewBox"].split(" ").map(v => +v);
					Object.assign(r.meta, {width : width-x, height : height-y});
				}
				else
				{
					if(imageInfo?.width && imageInfo?.height)	// this handles svg/23.svg which is missing a width tag but does have a height tag
						Object.assign(r.meta, {width : imageInfo.width, height : imageInfo.height});
					else
						Object.assign(r.meta, {width : 0, height : 0});
				}
			}
			catch
			{
				Object.assign(r.meta, {width : 0, height : 0});
			}
		}
	};
	renameOut = false;
}
