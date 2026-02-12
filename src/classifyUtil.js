import {xu} from "xu";
import {runUtil, fileUtil} from "xutil";
import {path} from "std";
import {Program} from "./Program.js";
import {DexFile} from "./DexFile.js";
import {C} from "./C.js";

const MODEL_DIM =
{
	garbage : [300, 300]
};

const RUN_OPTIONS = {timeout : xu.MINUTE*2};

const CROP_METHODS = ["centerCrop", "scaleDown"];
async function cropImage({modelName, inPath, outPath, method="centerCrop"}={})
{
	if(!["centerCrop", "scaleDown", "smartCrop"].includes(method))
		throw new Error(`Invalid classifyUtil cropImage method: ${method}`);

	if(method==="smartCrop")
		await runUtil.run("smartcrop", [inPath, outPath, MODEL_DIM[modelName].join("x")], RUN_OPTIONS);
	else if(method==="scaleDown")
		await runUtil.run("magick", [inPath, "-background", "transparent", "-gravity", "center", "-resize", `${MODEL_DIM[modelName].join("x")}>`, "-extent", MODEL_DIM[modelName].join("x"), "+repage", outPath], RUN_OPTIONS);
	else if(method==="centerCrop")
		await runUtil.run("magick", [inPath, "-background", "transparent", "-gravity", "center", "-crop", `${MODEL_DIM[modelName].join("x")}+0+0`, "-extent", MODEL_DIM[modelName].join("x"), "+repage", outPath], RUN_OPTIONS);
}

export async function preProcessPNG(modelName, imagePath, outDir)
{
	await Deno.mkdir(path.join(C.CLASSIFY_PATH, "tmp"), {recursive : true});
	const pngTrimmedPath = await fileUtil.genTempPath(path.join(C.CLASSIFY_PATH, "tmp"), ".png");
	await runUtil.run("magick", [`./${path.basename(imagePath)}[0]`, pngTrimmedPath], {...RUN_OPTIONS, cwd : path.dirname(imagePath)});	// We use [0] just in case the src image is an animation, so we just use the first frame
	
	const tmpTrimPath = await fileUtil.genTempPath(path.join(C.CLASSIFY_PATH, "tmp"), ".png");
	await runUtil.run("magick", ["-define", "filename:literal=true", "-define", "png:exclude-chunks=time", pngTrimmedPath, "-trim", "+repage", `PNG:${tmpTrimPath}`]);
	await fileUtil.move(tmpTrimPath, pngTrimmedPath);

	for(const CROP_METHOD of CROP_METHODS)
		await cropImage({modelName, inPath : pngTrimmedPath, outPath : path.join(outDir, `${CROP_METHOD}_${path.basename(imagePath)}.png`), method : CROP_METHOD});
}

export async function classifyImage(imagePath, modelName, xlog)
{
	const tmpImagePaths = await Promise.all(CROP_METHODS.map(v => fileUtil.genTempPath(path.join(C.CLASSIFY_PATH, "tmp"), `_${v}.png`)));

	// convert to PNG
	const pngTrimmedPath = await fileUtil.genTempPath(path.join(C.CLASSIFY_PATH, "tmp"), ".png");

	const fileR = await Program.runProgram("file", await DexFile.create({root : path.dirname(imagePath), absolute : imagePath}), {xlog, autoUnlink : true});
	
	// We do the cwd and leading ./ to handle files that start with dashes
	if(fileR?.meta?.detections?.some(o => o.value.startsWith("SVG Scalable Vector Graphics image")))	// eslint-disable-line unicorn/prefer-ternary
		await runUtil.run("inkscape", ["--export-area-drawing", "-o", pngTrimmedPath, `./${path.basename(imagePath)}`], {...RUN_OPTIONS, virtualX : true, cwd : path.dirname(imagePath)});
	else
		await runUtil.run("magick", [`./${path.basename(imagePath)}[0]`, pngTrimmedPath], {...RUN_OPTIONS, cwd : path.dirname(imagePath)});	// We use [0] just in case the src image is an animation, so we just use the first frame

	const tmpTrimPath = await fileUtil.genTempPath(path.join(C.CLASSIFY_PATH, "tmp"), ".png");
	await runUtil.run("magick", ["-define", "filename:literal=true", "-define", "png:exclude-chunks=time", pngTrimmedPath, "-trim", "+repage", `PNG:${tmpTrimPath}`]);
	await fileUtil.move(tmpTrimPath, pngTrimmedPath);

	const confidences = [];
	for(const [i, tmpImagePath] of tmpImagePaths.entries())
	{
		await cropImage({modelName, inPath : pngTrimmedPath, outPath : tmpImagePath, method : CROP_METHODS[i]});
		if(!await fileUtil.exists(tmpImagePath))
		{
			xlog.warn`Failed to crop image ${imagePath} for classification`;
			continue;
		}
		
		const garbageScore = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${C.CLASSIFY_HOST}:${C.CLASSIFY_PORT}/classify/${modelName}`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify({imagePath : tmpImagePath})}))?.json()), {});
		await fileUtil.unlink(tmpImagePath);
		confidences.push(garbageScore);
	}

	await fileUtil.unlink(pngTrimmedPath);
	return confidences.average();
}
