/* global window */
import {xu} from "xu";
import {fileUtil, runUtil, cmdUtil} from "xutil";
import {base64Encode, base64Decode, path} from "std";
import {C} from "../src/C.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "poly2thumb",
	version : "1.0.0",
	desc    : "Converts a polygon into a thumbnail",
	opts    :
	{
		fps                : {desc : "How many FPS", hasValue : true, defaultValue : C.POLY_THUMB_DEFAULT_FPS},
		rotateSpeed        : {desc : "How fast to rotate the model in degrees per second", hasValue : true, defaultValue : C.POLY_THUMB_DEFAULT_ROTATE_SPEED},
		thumbWidth         : {desc : "The width of the thumbnail", hasValue : true, defaultValue : C.POLY_THUMB_WIDTH},
		thumbHeight        : {desc : "The height of the thumbnail", hasValue : true, defaultValue : C.POLY_THUMB_HEIGHT},
		maxAttemptDuration : {desc : "The maximum duration in ms that we will wait to get all frames to capture a smooth 360 rotation before giving up and filling in blanks", hasValue : true, defaultValue : xu.SECOND*40},
		tmpDirPath         : {desc : "The path to the temp directory", hasValue : true, defaultValue : "/mnt/ram/tmp"}
	},
	args :
	[
		{argid : "polyFilePath", desc : "Disk path to the poly", required : true},
		{argid : "thumbFilePath", desc : "Disk path to the thumbnail", required : true}
	]});

if(!argv.thumbFilePath.startsWith("/"))
	argv.thumbFilePath = path.resolve(argv.thumbFilePath);

// deno-lint-ignore no-import-prefix
import {launch} from "jsr:@astral/astral@0.4.8";

const desiredFrameCount = (360/argv.rotateSpeed)*argv.fps;

const tmpHTMLFilePath = await fileUtil.genTempPath(undefined, ".html");
await fileUtil.writeTextFile(tmpHTMLFilePath, `
	<html>
		<head></head>
		<body>
			<script type="module">${await fileUtil.readTextFile(path.join(import.meta.dirname, "aux", "model-viewer.min.js"))}</script>
			<span id="modelHolder"></span>
			<script type="module">
				addEventListener("DOMContentLoaded", () =>
				{
					if(!customElements || !customElements.get("model-viewer"))
						return;

					// this line will ensure the model is always rendered at 100% scale, which is important for the thumbnail
					// this can cause the rotation to be pretty slow if the computer is busy, but we'll just have to live with that for huge models
					customElements.get("model-viewer").minimumRenderScale = 1;

					document.querySelector("#modelHolder").innerHTML = '<model-viewer style="width: ${argv.thumbWidth}px; height: ${argv.thumbHeight}px;" loading="eager" reveal="auto" interaction-prompt="none" auto-rotate auto-rotate-delay="0" rotation-per-second="${argv.rotateSpeed}deg" src="data:model/gltf-binary;base64,${base64Encode(await Deno.readFile(argv.polyFilePath))}" shadow-intensity="0"></model-viewer>';

					const modelViewer = document.querySelector("model-viewer");
					modelViewer.addEventListener("load", () =>
					{
						const desiredFrameCount = ${desiredFrameCount};
						const pngFrames = new Array(desiredFrameCount).fill(null);
						const degreesPerFrame = 360/desiredFrameCount;
						let frameCount = 0;
						const startedAt = performance.now();

						function raf()
						{
							const idealFrame = Math.floor((((modelViewer.turntableRotation * 180 / Math.PI) % 360 + 360) % 360)/degreesPerFrame);
							if(pngFrames[idealFrame]===null)
							{
								pngFrames[idealFrame] = modelViewer.toDataURL("image/png");
								frameCount++;
							}

							if(frameCount>=desiredFrameCount || performance.now()-startedAt>${argv.maxAttemptDuration})
							{
								window.renderDataJSON = JSON.stringify({frames : pngFrames});
								return;
							}

							requestAnimationFrame(raf);
						}
						requestAnimationFrame(raf);
					});
				});
			</script>
	</html>`);

// astral uses a lot of temp space, sometimes our main disk at /tmp doesn't have a lot, so make sure it uses /mnt/ram/tmp where we'll have plenty
const userDataDir = await fileUtil.genTempPath(argv.tmpDirPath, "poly2thumb-chrome-user-data");
await Deno.mkdir(userDataDir, {recursive : true});
const browser = await launch({args : [`--user-data-dir=${userDataDir}`]});

// some glbs don't load correctly (poly/glTF/bad.glb) and the browser just hangs, so we give up after a certain amount of time
let browserClosed = false;
const closeBrowserTimeout = setTimeout(async () =>
{
	await browser.close();
	browserClosed = true;
}, argv.maxAttemptDuration+(xu.SECOND*5));

const page = await browser.newPage(`file://${tmpHTMLFilePath}`);
let renderDataJSON = null;
await xu.waitUntil(async () =>
{
	// deno-lint-ignore no-window
	renderDataJSON = await xu.tryFallbackAsync(async () => await page.evaluate(() => (window.renderDataJSON || null)), "null");
	return !!renderDataJSON;
});

if(!browserClosed)
{
	clearTimeout(closeBrowserTimeout);
	await browser.close();
}
await fileUtil.unlink(tmpHTMLFilePath);

const renderData = xu.parseJSON(renderDataJSON);
if(renderData?.frames?.length)
{
	// if the computer is super slow right now, we may not have very many frames that represent the entire rotation, so just fill in the missing frames to ensure a full rotation
	let lastFrame=renderData.frames.find(v => v!==null);
	for(let i=0;i<renderData.frames.length;i++)
	{
		if(renderData.frames[i]===null)
			renderData.frames[i] = lastFrame;
		else
			lastFrame = renderData.frames[i];
	}

	const framesDirPath = await fileUtil.genTempPath();
	await Deno.mkdir(framesDirPath);
	await Object.entries(renderData.frames).parallelMap(async ([i, pngFrame]) =>
	{
		const framePath = path.join(framesDirPath, i.toString());
		await Deno.writeFile(`${framePath}.png`, base64Decode(pngFrame.substring(pngFrame.indexOf("base64,")+"base64,".length)));
		await runUtil.run("magick", [`${framePath}.png`, `${framePath}.gif`], {liveOutput : true});
	}, -1);

	const tmpGIFFilePath = await fileUtil.genTempPath(undefined, ".gif");
	await runUtil.run("gifsicle", ["--loop", "--disposal=background", "--colors", "256", `--delay=${Math.floor((1/argv.fps)*100)}`, ...[].pushSequence(0, renderData.frames.length-1).map(v => `${v}.gif`), "-o", tmpGIFFilePath], {cwd : framesDirPath, liveOutput : true});
	await fileUtil.move(tmpGIFFilePath, argv.thumbFilePath);
	await fileUtil.unlink(framesDirPath, {recursive : true});
}

await xu.tryFallbackAsync(async () => await fileUtil.unlink(userDataDir, {recursive : true}));
