/* global window */
import {xu} from "xu";
import {fileUtil, runUtil, cmdUtil} from "xutil";
import {C} from "./ppUtil.js";
import {base64Encode, base64Decode, path} from "std";

const argv = cmdUtil.cmdInit({
	cmdid   : "poly2thumbStatic",
	version : "1.0.0",
	desc    : "Converts a polygon into a thumbnail",
	opts    :
	{
		thumbWidth         : {desc : "The width of the thumbnail", hasValue : true, defaultValue : C.POLY_THUMB_WIDTH},
		thumbHeight        : {desc : "The height of the thumbnail", hasValue : true, defaultValue : C.POLY_THUMB_HEIGHT},
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

const tmpHTMLFilePath = await fileUtil.genTempPath(undefined, ".html");
await fileUtil.writeTextFile(tmpHTMLFilePath, `
	<html>
		<head></head>
		<body>
			<script type="module">${await fileUtil.readTextFile(path.join(import.meta.dirname, "..", "root", "js", "model-viewer.min.js"))}</script>
			<span id="modelHolder"></span>
			<script type="module">
				addEventListener("DOMContentLoaded", () =>
				{
					if(!customElements || !customElements.get("model-viewer"))
						return;

					// this line will ensure the model is always rendered at 100% scale, which is important for the thumbnail
					customElements.get("model-viewer").minimumRenderScale = 1;

					document.querySelector("#modelHolder").innerHTML = '<model-viewer style="width: ${argv.thumbWidth}px; height: ${argv.thumbHeight}px;" loading="eager" reveal="auto" interaction-prompt="none" src="data:model/gltf-binary;base64,${base64Encode(await Deno.readFile(argv.polyFilePath))}" shadow-intensity="0"></model-viewer>';

					const modelViewer = document.querySelector("model-viewer");
					modelViewer.addEventListener("load", () =>
					{
						window.renderDataRaw = modelViewer.toDataURL("image/png");
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
}, xu.MINUTE);

const page = await browser.newPage(`file://${tmpHTMLFilePath}`);
let renderDataRaw = null;
await xu.waitUntil(async () =>
{
	// deno-lint-ignore no-window
	renderDataRaw = await xu.tryFallbackAsync(async () => await page.evaluate(() => (window.renderDataRaw || null)), "null");
	return !!renderDataRaw;
});

if(!browserClosed)
{
	clearTimeout(closeBrowserTimeout);
	await browser.close();
}
await fileUtil.unlink(tmpHTMLFilePath);

if(renderDataRaw)
{
	const frameFilePath = await fileUtil.genTempPath();
	await Deno.writeFile(`${frameFilePath}.png`, base64Decode(renderDataRaw.substring(renderDataRaw.indexOf("base64,")+"base64,".length)));
	await runUtil.run("magick", [...C.CONVERT_PNG_ARGS, `${frameFilePath}.png`, `PNG:${argv.thumbFilePath}`], {liveOutput : true});
	await fileUtil.unlink(frameFilePath, {recursive : true});
}

await xu.tryFallbackAsync(async () => await fileUtil.unlink(userDataDir, {recursive : true}));
