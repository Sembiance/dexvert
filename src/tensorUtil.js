import {xu} from "xu";
import {runUtil, fileUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import {identify} from "./identify.js";

export const TENSORSERV_PATH = "/mnt/ram/dexvert/tensor";
export const TENSORSERV_HOST = "localhost";
export const TENSORSERV_PORT = 17736;

const TENSOR_DIM = [224, 224];
const RUN_OPTIONS = {timeout : xu.MINUTE*2};

async function cropImage({inPath, outPath, method="centerCrop"}={})
{
	if(!["centerCrop", "scaleDown", "smartCrop"].includes(method))
		throw new Error(`Invalid tensorUtil cropImage method: ${method}`);

	if(method==="smartCrop")
		await runUtil.run("smartcrop", [inPath, outPath, TENSOR_DIM.join("x")], RUN_OPTIONS);
	else if(method==="scaleDown")
		await runUtil.run("convert", [inPath, "-background", "transparent", "-gravity", "center", "-resize", `${TENSOR_DIM.join("x")}>`, "-extent", TENSOR_DIM.join("x"), "+repage", outPath], RUN_OPTIONS);
	else if(method==="centerCrop")
		await runUtil.run("convert", [inPath, "-background", "transparent", "-gravity", "center", "-crop", `${TENSOR_DIM.join("x")}+0+0`, "-extent", TENSOR_DIM.join("x"), "+repage", outPath], RUN_OPTIONS);
}

export async function classifyImage(imagePath, modelName)
{
	const CROP_METHODS = ["centerCrop", "scaleDown"];
	const tmpImagePaths = await Promise.all(CROP_METHODS.map(v => fileUtil.genTempPath(path.join(TENSORSERV_PATH, "tmp"), `_${v}.png`)));

	// convert to PNG
	const pngTrimmedPath = await fileUtil.genTempPath(path.join(TENSORSERV_PATH, "tmp"), ".png");

	const identifications = await identify(imagePath);

	// We do the cwd and leading ./ to handle files that start with dashes
	if(identifications.some(o => o.formatid==="svg"))	// eslint-disable-line unicorn/prefer-ternary
		await runUtil.run("inkscape", ["--export-area-drawing", "-o", pngTrimmedPath, `./${path.basename(imagePath)}`], {...RUN_OPTIONS, virtualX : true, cwd : path.dirname(imagePath)});
	else
		await runUtil.run("convert", [`./${path.basename(imagePath)}[0]`, pngTrimmedPath], {...RUN_OPTIONS, cwd : path.dirname(imagePath)});	// We use [0] just in case the src image is an animation, so we just use the first frame

	await runUtil.run("autocrop", [pngTrimmedPath], RUN_OPTIONS);

	const confidences = [];
	for(const [i, tmpImagePath] of tmpImagePaths.entries())
	{
		await cropImage({inPath : pngTrimmedPath, outPath : tmpImagePath, method : CROP_METHODS[i]});
		if(!(await fileUtil.exists(tmpImagePath)))
			continue;
		
		const r = (await (await fetch(`http://${TENSORSERV_HOST}:${TENSORSERV_PORT}/classify/${modelName}`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify({imagePath : tmpImagePath})}))?.json()) || {};

		await fileUtil.unlink(tmpImagePath);
		
		if(r?.Confidences.length===2)
			confidences.push(r.Confidences[0]);
	}

	await fileUtil.unlink(pngTrimmedPath);

	return confidences.average();
}
