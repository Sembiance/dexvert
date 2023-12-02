import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {xmlParse} from "denoLandX";
import {path, base64Encode} from "std";

export class fig2dev extends Program
{
	website = "https://www.xfig.org/";
	package = "media-gfx/fig2dev";
	flags   = {
		outType : `Which image format to convert to (png for example). Default: svg`
	};
	notes = "The output SVG has it's external image file references replaced with the base64 data uri, but this of course means only images supported by the browser/svg reader will be able to viewed. I could convert all images with dexvert first, but MEH.";
	bin   = "fig2dev";
	args  = async r => ["-L", (r.flags.outType || "svg"), r.inFile(), await r.outFile(`out.${r.flags.outType || "svg"}`)];
	post  = async r =>
	{
		// inline into the SVG any referenced images
		const svgOutFile = (r.f.files.output || []).find(file => file.ext.toLowerCase()===".svg");
		if(!svgOutFile)
			return;

		let svgFileData = await fileUtil.readTextFile(svgOutFile.absolute);
		const svgData = xmlParse(svgFileData);
		await Object.findReplace(svgData, (k, v) => (Object.isObject(v) && Object.hasOwn(v, "@xlink:href") && v["@xlink:href"].startsWith("file://")), async (k, v) =>
		{
			const xlinkHref = v["@xlink:href"];
			const filePath = path.resolve(r.f.root, xlinkHref.substring("file://".length));
			if(!await fileUtil.exists(filePath))
				return v;
			
			// Did try just modifying the object and then doing xmlStringify() below when saving the file, sadly the xml module is not reliable, especially when stringifying, it failed to produce the same output
			svgFileData = svgFileData.replaceAll(xlinkHref, `data:image;base64,${base64Encode(await Deno.readFile(filePath))}`);

			return v;
		});

		await fileUtil.writeTextFile(svgOutFile.absolute, svgFileData);
	};

	renameOut = true;
	chain     = r => ((r.flags.outType || "svg")==="svg" ? `deDynamicSVG${r.flags.autoCropSVG ? "[autoCrop]" : ""}` : null);
}
